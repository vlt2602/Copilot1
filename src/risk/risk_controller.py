class RiskController:
    def __init__(self, config):
        self.config = config
        self.safe_mode = False

    def check_risk(self, trade_result, ai_status, market_volatility):
        # TODO: kiểm tra các điều kiện kick SafeMode
        if ai_status == 'error' or trade_result == 'loss' or market_volatility == 'high':
            self.safe_mode = True
            print("SafeMode enabled!")
        else:
            self.safe_mode = False
        return self.safe_mode
