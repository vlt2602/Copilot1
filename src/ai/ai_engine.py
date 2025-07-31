import os
import pickle
import numpy as np
from utils.config_loader import ConfigLoader
from utils.log_manager import LogManager

class AIEngine:
    """
    AI Engine: quản lý load/call các model XGBoost, LSTM, RL,
    chuẩn hóa input/output, trả về tín hiệu duy nhất dạng ScoredSignal.
    """
    def __init__(self, model_dir="models", config_dir="config"):
        self.model_dir = model_dir
        self.config = ConfigLoader(config_dir)
        self.logger = LogManager.get_logger("ai")
        self.models = {}
        self.load_all_models()

    def load_model(self, model_type, symbol):
        """
        Load model từ file (pickle cho XGB/RL, H5 cho LSTM).
        """
        model_path = os.path.join(self.model_dir, f"{model_type}_{symbol}.pkl" if model_type != "lstm" else f"{model_type}_{symbol}.h5")
        if not os.path.exists(model_path):
            self.logger.error(f"Model file not found: {model_path}")
            return None
        if model_type == "lstm":
            from tensorflow.keras.models import load_model
            model = load_model(model_path)
        else:
            with open(model_path, "rb") as f:
                model = pickle.load(f)
        self.logger.info(f"Loaded {model_type} model for {symbol}")
        return model

    def load_all_models(self):
        """
        Load tất cả model đã train cho các symbol phổ biến.
        """
        for model_type in ["xgb", "lstm", "rl"]:
            self.models[model_type] = {}
            # Giả định có danh sách symbol trong config
            symbols = self.config.get("strategy", reload=True).get("symbols", ["BTCUSDT"])
            for symbol in symbols:
                model = self.load_model(model_type, symbol)
                if model:
                    self.models[model_type][symbol] = model

    def predict_xgb(self, symbol, features):
        model = self.models.get("xgb", {}).get(symbol)
        if not model:
            self.logger.error(f"No XGB model for {symbol}")
            return None
        proba = model.predict_proba([features])[0][1]
        return float(proba)

    def predict_lstm(self, symbol, series):
        model = self.models.get("lstm", {}).get(symbol)
        if not model:
            self.logger.error(f"No LSTM model for {symbol}")
            return None
        arr = np.array(series).reshape((1, len(series), 1))
        proba = model.predict(arr)[0][0]
        return float(proba)

    def predict_rl(self, symbol, state):
        model = self.models.get("rl", {}).get(symbol)
        if not model:
            self.logger.error(f"No RL model for {symbol}")
            return None
        # Giả lập: RL trả về Q-value hoặc xác suất hành động
        action_prob = model.predict([state])[0][1]
        return float(action_prob)

    def ensemble_predict(self, symbol, features, series, state):
        """
        Gộp kết quả các model (weighted average hoặc voting/logic bạn chọn).
        Trả về dict chuẩn hóa: ScoredSignal.
        """
        conf = self.config.get("ai", reload=True)
        xgb_thres = conf.get("xgb", {}).get("threshold", 0.6)
        lstm_thres = conf.get("lstm", {}).get("threshold", 0.7)
        xgb = self.predict_xgb(symbol, features)
        lstm = self.predict_lstm(symbol, series)
        rl = self.predict_rl(symbol, state)
        # Weighted confidence (tùy chỉnh logic)
        weighted = np.mean([x for x in [xgb, lstm, rl] if x is not None])
        signal = {
            "symbol": symbol,
            "xgb": xgb,
            "lstm": lstm,
            "rl": rl,
            "confidence": weighted,
            "pass": (xgb is not None and xgb > xgb_thres) and (lstm is not None and lstm > lstm_thres),
        }
        self.logger.info(f"AI Ensemble: {signal}")
        return signal

    def reload_models(self):
        """Reload all models (dùng khi retrain hoặc file mới)."""
        self.load_all_models()

# Usage example/test
if __name__ == "__main__":
    ai = AIEngine()
    # Giả lập input demo
    features = [0.1, 0.2, 0.3]
    series = [0.1]*50
    state = [0.2]*10
    pred = ai.ensemble_predict("BTCUSDT", features, series, state)
    print(pred)
