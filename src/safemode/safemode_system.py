import time
from utils.log_manager import LogManager

class SafeModeSystem:
    """
    Quản lý trạng thái SafeMode toàn hệ thống, chủ động bật/tắt khi có trigger,
    cảnh báo Discord/Admin, phối hợp với RiskController và các engine khác.
    """
    def __init__(self, risk_controller, discord_bot=None, cooldown_minutes=60):
        self.risk_controller = risk_controller
        self.discord_bot = discord_bot
        self.logger = LogManager.get_logger("safemode")
        self.cooldown_minutes = cooldown_minutes
        self.last_trigger_time = 0

    def should_enable(self, reason):
        """Xác định có nên bật SafeMode không?"""
        # Có thể mở rộng: check theo thời gian, số lần, loại trigger...
        now = time.time()
        if now - self.last_trigger_time < self.cooldown_minutes * 60:
            self.logger.info("SafeMode trigger ignored: cooldown not elapsed.")
            return False
        return True

    def enable(self, reason="manual"):
        if not self.should_enable(reason):
            return
        self.risk_controller.trigger_safe_mode(reason)
        self.last_trigger_time = time.time()
        self.logger.warning(f"SAFE MODE ENABLED: {reason}")
        if self.discord_bot:
            try:
                msg = f":rotating_light: **SAFE MODE ENABLED**\nReason: {reason}\nAll trading paused for {self.cooldown_minutes} minutes."
                # Gửi notify async (Streamlit/Discord bot thread-safe)
                import asyncio
                asyncio.create_task(self.discord_bot.notify(msg))
            except Exception as e:
                self.logger.error(f"Cannot notify Discord: {e}")

    def disable(self, notify=True):
        self.risk_controller.safe_mode = False
        self.logger.info("SAFE MODE DISABLED: Trading resumed.")
        if self.discord_bot and notify:
            try:
                msg = ":white_check_mark: **SAFE MODE DISABLED**\nBot trading will resume."
                import asyncio
                asyncio.create_task(self.discord_bot.notify(msg))
            except Exception as e:
                self.logger.error(f"Cannot notify Discord: {e}")

    def auto_monitor(self):
        """
        Worker loop: tự động theo dõi trạng thái risk, bật/tắt SafeMode khi cần.
        Có thể chạy nền bằng thread hoặc asyncio task.
        """
        try:
            while True:
                # Check risk triggers liên tục
                risk = self.risk_controller.report()
                if risk.get("safe_mode") and time.time() > self.risk_controller.safe_mode_until:
                    self.disable()
                # Có thể bổ sung thêm các logic khác, ví dụ:
                # - Nếu drawdown vượt ngưỡng, enable SafeMode
                # - Nếu chuỗi lỗi lớn, enable SafeMode
                # - Nếu nhận tín hiệu từ Discord/Webhook, enable SafeMode
                time.sleep(10)
        except KeyboardInterrupt:
            self.logger.info("SafeMode monitoring stopped.")

# Usage example/test
if __name__ == "__main__":
    from risk.risk_controller import RiskController

    class DummyDiscord:
        async def notify(self, msg): print("Discord notify:", msg)

    rc = RiskController()
    sd = SafeModeSystem(rc, DummyDiscord(), cooldown_minutes=1)
    sd.enable("test drawdown")
    time.sleep(2)
    sd.disable()
