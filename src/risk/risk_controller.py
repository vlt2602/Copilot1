import time
from utils.config_loader import ConfigLoader
from utils.log_manager import LogManager

class RiskController:
    """
    Quản lý SafeMode, kiểm soát drawdown, max position, stop-loss động, trigger cảnh báo.
    Đảm bảo an toàn vốn và quản lý rủi ro realtime.
    """
    def __init__(self, config_dir="config"):
        self.config = ConfigLoader(config_dir)
        self.logger = LogManager.get_logger("risk")
        self.reload_config()
        self.safe_mode = False
        self.safe_mode_until = 0
        self.error_count = 0
        self.loss_streak = 0
        self.drawdown = 0.0
        self.day_loss = 0.0

    def reload_config(self):
        cfg = self.config.get("risk", reload=True)
        self.risk_cfg = cfg.get("risk_control", {})
        self.max_daily_loss = self.risk_cfg.get("max_daily_loss", 5.0) / 100.0
        self.max_position_size = self.risk_cfg.get("max_position_size", 10.0) / 100.0
        self.safe_mode_triggers = self.risk_cfg.get("safe_mode_triggers", ["ai_error", "continuous_loss", "high_atr_spike"])
        self.safe_mode_period = self.risk_cfg.get("disable_after_minutes", 60)

    def check_max_position(self, size, balance):
        ok = size <= balance * self.max_position_size
        if not ok:
            self.logger.warning(f"Position size {size} over limit {balance * self.max_position_size}")
        return ok

    def check_drawdown(self, current_balance, start_balance):
        self.drawdown = (start_balance - current_balance) / start_balance
        if self.drawdown > self.max_daily_loss:
            self.logger.warning(f"Drawdown exceeded: {self.drawdown:.2%}")
            self.trigger_safe_mode("drawdown_exceeded")
            return False
        return True

    def on_trade_result(self, pnl):
        # Theo dõi thua liên tiếp
        if pnl < 0:
            self.loss_streak += 1
        else:
            self.loss_streak = 0
        # Auto SafeMode nếu thua liên tiếp 3 lệnh
        if self.loss_streak >= 3 and "continuous_loss" in self.safe_mode_triggers:
            self.trigger_safe_mode("continuous_loss")

    def on_ai_error(self):
        self.error_count += 1
        if self.error_count >= 2 and "ai_error" in self.safe_mode_triggers:
            self.trigger_safe_mode("ai_error")

    def on_atr_spike(self, atr, threshold):
        if atr > threshold and "high_atr_spike" in self.safe_mode_triggers:
            self.trigger_safe_mode("high_atr_spike")

    def trigger_safe_mode(self, reason):
        self.safe_mode = True
        self.safe_mode_until = time.time() + self.safe_mode_period * 60
        self.logger.error(f"SAFE MODE TRIGGERED: {reason}. All trading halted for {self.safe_mode_period} minutes.")

    def check_safe_mode(self):
        if self.safe_mode and time.time() > self.safe_mode_until:
            self.safe_mode = False
            self.error_count = 0
            self.loss_streak = 0
            self.logger.info("SAFE MODE DISABLED: Trading resumed.")
        return self.safe_mode

    def should_trade(self):
        return not self.check_safe_mode()

    def report(self):
        status = {
            "safe_mode": self.safe_mode,
            "safe_mode_until": self.safe_mode_until,
            "loss_streak": self.loss_streak,
            "drawdown": round(self.drawdown, 4),
            "error_count": self.error_count,
        }
        self.logger.info(f"Risk report: {status}")
        return status

# Usage example/test
if __name__ == "__main__":
    rc = RiskController()
    rc.on_trade_result(-50)
    rc.on_trade_result(-30)
    rc.on_trade_result(-10)  # Should trigger SafeMode
    print(rc.report())
    print("Should trade?", rc.should_trade())
