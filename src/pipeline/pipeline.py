from src.ai.ai_trainer import AITrainer
from src.risk.risk_controller import RiskController

class Pipeline:
    def __init__(self, config):
        self.config = config
        self.ai_trainer = AITrainer('xgb', config['xgb'])
        self.risk_controller = RiskController(config['risk'])

    def fetch_data(self):
        # TODO: Fetch candle data
        return [], []
    def preprocess(self, X, y):
        # TODO: Preprocess data
        return X, y
    def run(self):
        X, y = self.fetch_data()
        X, y = self.preprocess(X, y)
        self.ai_trainer.train(X, y)
        signal = self.ai_trainer.predict(X)
        safe_mode = self.risk_controller.check_safe_mode(['win','loss','loss'], 'ok', 10)
        if safe_mode:
            print('SafeMode active. Skip trade!')
        else:
            print(f'Execute trade with signal: {signal}')
