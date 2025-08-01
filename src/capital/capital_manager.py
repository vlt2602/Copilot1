import math
from utils.config_loader import ConfigLoader
from utils.log_manager import LogManager

class CapitalManager:
    """
    Quản lý vốn, position sizing (Kelly/fixed), scaling (pyramiding),
    theo dõi PnL, cập nhật balance và báo cáo vốn cho các module khác.
    """
    def __init__(self, config_dir="config"):
        self.config = ConfigLoader(config_dir)
        self.logger = LogManager.get_logger("capital")
        self.reset_state()

        cfg = self.config.get("strategy", reload=True)

        # Đọc thông số từ strategy.yaml
        self.max_position_pct = cfg.get("strategy", {}).get("max_position_size", 4.0) / 100.0
        self.kelly_fraction = cfg.get("strategy", {}).get("kelly_fraction", 0.12)

    def reset_state(self):
        self.balance = 10000.0  # Khởi tạo giả định, cần lấy từ API thực tế
        self.equity = self.balance
        self.open_positions = []
        self.total_pnl = 0.0
        self.daily_pnl = 0.0
        self.current_day = None

    def update_balance(self, realized_pnl, day=None):
        if day and day != self.current_day:
            self.daily_pnl = 0.0
            self.current_day = day
        self.balance += realized_pnl
        self.daily_pnl += realized_pnl
        self.total_pnl += realized_pnl
        self.logger.info(f"Balance updated: {self.balance:.2f}, Daily PnL: {self.daily_pnl:.2f}")

    def kelly_position_size(self, winrate, rr, risk_pct=None):
        """
        Tính position size theo Kelly Criterion:
        Kelly = W - (1-W)/R, W: winrate, R: reward/risk
        """
        fraction = self.kelly_fraction
        kelly = winrate - (1 - winrate) / rr if rr > 0 else 0
        kelly = max(0, min(kelly, 1))  # Clamp 0-1
        risk_pct = fraction if risk_pct is None else risk_pct
        size = self.balance * min(kelly * risk_pct, self.max_position_pct)
        self.logger.debug(f"Kelly size: {size:.2f} ({kelly=:.2f}, {risk_pct=:.2f})")
        return round(size, 2)

    def fixed_position_size(self, risk_pct=None):
        risk_pct = risk_pct if risk_pct is not None else self.kelly_fraction
        size = self.balance * min(risk_pct, self.max_position_pct)
        self.logger.debug(f"Fixed size: {size:.2f} ({risk_pct=:.2f})")
        return round(size, 2)

    def get_position_size(self, strategy_stats, method=None, risk_pct=None):
        """
        strategy_stats: dict with keys 'winrate', 'rr'
        """
        method = method or self.config.get("strategy", {}).get("strategy", {}).get("position_sizing_method", "kelly")
        if method == "kelly":
            return self.kelly_position_size(
                strategy_stats.get("winrate", 0.55),
                strategy_stats.get("rr", 2.0),
                risk_pct if risk_pct is not None else self.kelly_fraction
            )
        else:
            return self.fixed_position_size(risk_pct)

    def add_position(self, symbol, size, entry_price, side):
        pos = {"symbol": symbol, "size": size, "entry": entry_price, "side": side}
        self.open_positions.append(pos)
        self.logger.info(f"Opened {side} {symbol} size {size} at {entry_price}")

    def close_position(self, pos_idx, exit_price):
        pos = self.open_positions[pos_idx]
        pnl = (exit_price - pos["entry"]) * pos["size"] if pos["side"] == "buy" else (pos["entry"] - exit_price) * pos["size"]
        self.update_balance(pnl)
        self.logger.info(f"Closed {pos['side']} {pos['symbol']} at {exit_price}, PnL: {pnl:.2f}")
        del self.open_positions[pos_idx]
        return pnl

    def scale_position(self, symbol, add_size, entry_price, side):
        """
        Pyramiding: thêm vị thế mới cùng chiều
        """
        self.add_position(symbol, add_size, entry_price, side)
        self.logger.info(f"Pyramiding {side} {symbol}: +{add_size} at {entry_price}")

    def report(self):
        report = {
            "balance": round(self.balance, 2),
            "daily_pnl": round(self.daily_pnl, 2),
            "total_pnl": round(self.total_pnl, 2),
            "open_positions": list(self.open_positions)
        }
        self.logger.info(f"Capital Report: {report}")
        return report

# Usage example/test
if __name__ == "__main__":
    cm = CapitalManager()
    stats = {"winrate": 0.60, "rr": 2.0}
    size = cm.get_position_size(stats)
    cm.add_position("BTCUSDT", size, 29000, "buy")
    pnl = cm.close_position(0, 29200)
    print("PnL Closed:", pnl)
    print("Report:", cm.report())
