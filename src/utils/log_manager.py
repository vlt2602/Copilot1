import os
import logging
from logging.handlers import RotatingFileHandler

class LogManager:
    """
    Centralized log manager. 
    Each module can get its own logger by name.
    Logs are rotated, formatted, and stored by module in /logs/.
    """
    LOG_DIR = "logs"
    MAX_BYTES = 2 * 1024 * 1024   # 2MB/file
    BACKUP_COUNT = 3              # Keep 3 old logs

    @staticmethod
    def get_logger(module_name: str, level=logging.INFO):
        """Return a logger for a specific module (ai, signal, order, error, main...)."""
        if not os.path.exists(LogManager.LOG_DIR):
            os.makedirs(LogManager.LOG_DIR)
        log_path = os.path.join(LogManager.LOG_DIR, f"{module_name}.log")
        logger = logging.getLogger(module_name)
        if not logger.handlers:
            handler = RotatingFileHandler(log_path, maxBytes=LogManager.MAX_BYTES, backupCount=LogManager.BACKUP_COUNT)
            formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(level)
            # Optional: also log to console (remove if not needed)
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            logger.addHandler(ch)
        return logger

# Usage example
if __name__ == "__main__":
    logger = LogManager.get_logger("main")
    logger.info("THopper PRO++ logging system initialized.")
    logger.error("This is a test error log.")
