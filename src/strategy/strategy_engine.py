import numpy as np
from utils.config_loader import ConfigLoader
from utils.log_manager import LogManager

class StrategyEngine:
    """
    Quản lý các chiến lược trading, áp dụng tín hiệu AI, chọn lệnh, lọc symbol.
    Hỗ trợ multi-strategy, trailing, coin filter, DCA, copytrade.
    """
    def __init__(self, config_dir="config"):
        self.config = ConfigLoader(config_dir)
        self.logger = LogManager.get_logger("strategy")
        self.reload_config()

    def reload_config(self):
        self.strategy_cfg = self.config.get("strategy", reload=True)
        self.advanced_cfg = self.strategy_cfg.get("coin_filter_advanced", {})
        self.available_strategies = self.strategy_cfg.get("available_strategies", ["rsi_macd"])

    def check_filter(self, symbol, candles, side):
        """
        Lọc symbol theo volume, banned keyword, ratio, etc.
        """
        # Volume filter
        if self.advanced_cfg.get("enabled", False):
            tf = self.strategy_cfg.get("timeframe", "1h")
            min_vol = self.advanced_cfg.get(f"min_buy_volume_usdt_{tf}", 0)
            last_vol = candles[-1]["quote_volume"] if "quote_volume" in candles[-1] else candles[-1].get("volume", 0)
            if last_vol < min_vol:
                self.logger.debug(f"{symbol} filtered by volume: {last_vol}<{min_vol}")
                return False
            # Ratio logic
            # (Có thể mở rộng: prefer_buy_ratio, exclude_if_sell_ratio, ...)
        # Banned keyword
        for bad in self.strategy_cfg.get("banned_keywords", []):
            if bad in symbol:
                self.logger.debug(f"{symbol} filtered by banned keyword: {bad}")
                return False
        # Side check
        allowed_side = self.strategy_cfg.get("allowed_side", ["buy", "sell"])
        if side not in allowed_side:
            self.logger.debug(f"{symbol} side {side} not allowed")
            return False
        return True

    def apply_rsi_macd(self, candles):
        """
        RSI-MACD strategy: trả về side, confidence, SL/TP, trailing...
        """
        closes = np.array([c["close"] for c in candles[-30:]])
        # Tính RSI
        delta = np.diff(closes)
        gain = np.mean(delta[delta > 0]) if np.any(delta > 0) else 0
        loss = -np.mean(delta[delta < 0]) if np.any(delta < 0) else 0
        rs = gain / loss if loss > 0 else 0
        rsi = 100 - (100 / (1 + rs)) if loss > 0 else 100
        # Tính MACD (đơn giản)
        ema12 = np.mean(closes[-12:])
        ema26 = np.mean(closes[-26:])
        macd = ema12 - ema26
        # Điều kiện vào lệnh
        if rsi < 30 and macd > 0:
            return "buy", rsi, macd
        elif rsi > 70 and macd < 0:
            return "sell", rsi, macd
        else:
            return None, rsi, macd

    def propose_trade(self, ai_signal, candles, strategy_stats=None):
        """
        Đầu vào: ai_signal (ScoredSignal), candles (list), strategy_stats (dict).
        Đầu ra: dict đề xuất lệnh chuẩn hóa cho Execution Engine.
        """
        self.reload_config()
        symbol = ai_signal["symbol"]
        tf = self.strategy_cfg.get("timeframe", "1h")
        confidence_thres = self.strategy_cfg.get("confidence_threshold", 0.7)
        # Chọn chiến lược
        strat_name = self.strategy_cfg.get("name", "rsi_macd")
        side, rsi, macd = None, None, None
        if strat_name == "rsi_macd":
            side, rsi, macd = self.apply_rsi_macd(candles)
        # Có thể mở rộng nhiều strategy khác tại đây...

        # Nếu AI pass và chiến lược thỏa điều kiện
        if ai_signal["pass"] and side and ai_signal["confidence"] > confidence_thres:
            if not self.check_filter(symbol, candles, side):
                return None
            sl = self.strategy_cfg.get("sl", 2.5)
            tp = self.strategy_cfg.get("tp", 5.0)
            trailing_cfg = self.strategy_cfg.get("trailing", {})
            proposal = {
                "symbol": symbol,
                "side": side,
                "confidence": ai_signal["confidence"],
                "strategy": strat_name,
                "sl": sl,
                "tp": tp,
                "trailing": trailing_cfg,
                "info": {"rsi": rsi, "macd": macd}
            }
            self.logger.info(f"Proposed trade: {proposal}")
            return proposal
        else:
            self.logger.debug(f"No trade for {symbol}: pass={ai_signal['pass']} side={side} conf={ai_signal['confidence']:.2f}")
            return None

# Usage example/test
if __name__ == "__main__":
    import random
    # Giả lập nến
    candles = [{"close": 100 + random.uniform(-2, 2), "volume": 5000000} for _ in range(30)]
    ai_signal = {"symbol": "BTCUSDT", "xgb": 0.75, "lstm": 0.8, "rl": 0.7, "confidence": 0.75, "pass": True}
    se = StrategyEngine()
    prop = se.propose_trade(ai_signal, candles)
    print("Proposal:", prop)
