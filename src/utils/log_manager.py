import logging, os

class LogManager:
    def __init__(self, log_file='logs/thopper.log'):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        logging.basicConfig(filename=log_file, level=logging.INFO,
                            format='%(asctime)s %(levelname)s %(module)s: %(message)s')
    def info(self, module, msg):
        logging.info(f'[{module}] {msg}')
    def warning(self, module, msg):
        logging.warning(f'[{module}] {msg}')
    def error(self, module, msg):
        logging.error(f'[{module}] {msg}')
