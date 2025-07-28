import logging
class RiskController:
    def __init__(self, config):
        self.config = config
        self.safe_mode = False
        self.loss_count = 0
        self.ai_error_count = 0
        self.atr_spike = False

    def check_safe_mode(self, trade_results, ai_status, atr):
        if ai_status == 'error':
            self.ai_error_count += 1
        else:
            self.ai_error_count = 0
        if trade_results[-3:] == ['loss','loss','loss']:
            self.loss_count = 3
        else:
            self.loss_count = 0
        if atr > self.config.get('atr_threshold', 0):
            self.atr_spike = True
        if self.ai_error_count >= 2 or self.loss_count >= 3 or self.atr_spike:
            self.safe_mode = True
            logging.warning('SafeMode enabled!')
        else:
            self.safe_mode = False
        return self.safe_mode
