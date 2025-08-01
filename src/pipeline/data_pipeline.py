import threading
from collections import deque
from datetime import datetime
from typing import Dict, Deque, Any
from src.utils.config_loader import ConfigLoader
from src.utils.log_manager import LogManager

class CandleBuffer:
    """
    Quản lý buffer nến cho 1 symbol/timeframe.
    Tự động xóa 1000 nến cũ khi >max_candles.
    """
    def __init__(self, max_candles=4000):
        self.data: Deque[Dict[str, Any]] = deque()
        self.max_candles = max_candles
        self.lock = threading.Lock()

    def append(self, candle: dict):
        with self.lock:
            self.data.append(candle)
            if len(self.data) > self.max_candles:
                for _ in range(1000):
                    if self.data:
                        self.data.popleft()

    def get_data(self):
        with self.lock:
            return list(self.data)

    def __len__(self):
        return len(self.data)

class DataPipeline:
    """
    Quản lý toàn bộ dữ liệu nến (multi-symbol, multi-timeframe).
    Cung cấp API fetch, append, trigger cho các module khác.
    """
    def __init__(self, config_dir="config"):
        self.config = ConfigLoader(config_dir)
        cfg = self.config.get("strategy", reload=True)
        self.max_candles = cfg.get("data_fetcher", {}).get("max_candles", 4000)
        self.buffers: Dict[str, Dict[str, CandleBuffer]] = {}
        self.logger = LogManager.get_logger("data")

    def _get_buffer(self, symbol: str, timeframe: str):
        if symbol not in self.buffers:
            self.buffers[symbol] = {}
        if timeframe not in self.buffers[symbol]:
            self.buffers[symbol][timeframe] = CandleBuffer(max_candles=self.max_candles)
        return self.buffers[symbol][timeframe]

    def append_candle(self, symbol: str, timeframe: str, candle: dict):
        buf = self._get_buffer(symbol, timeframe)
        buf.append(candle)
        self.logger.debug(f"Appended candle for {symbol}-{timeframe}, total: {len(buf)}")

    def get_data(self, symbol: str, timeframe: str):
        buf = self._get_buffer(symbol, timeframe)
        return buf.get_data()

    def trigger_on_new_candle(self, symbol: str, timeframe: str, candle: dict, on_new=None):
        """
        Gọi khi có nến mới realtime. 
        Tự động append và gọi callback (on_new) nếu truyền vào (vd: trigger AI/strategy)
        """
        self.append_candle(symbol, timeframe, candle)
        if on_new:
            on_new(symbol, timeframe, self.get_data(symbol, timeframe))

# Usage example/test
if __name__ == "__main__":
    dp = DataPipeline()
    dp.append_candle("BTCUSDT", "15m", {"timestamp": datetime.utcnow().isoformat(), "open": 29000, "high": 29100, "low": 28900, "close": 29050, "volume": 120})
    print(dp.get_data("BTCUSDT", "15m"))
