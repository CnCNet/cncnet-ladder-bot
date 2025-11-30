from logging.handlers import RotatingFileHandler
import logging


class MyLogger:
    MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT = 3

    def __init__(self, name, debug_log_filename='logs/debug.log', info_log_filename='logs/info.log'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Only add handlers if not already present (prevents duplicate handlers)
        if not self.logger.handlers:
            # Rotating debug handler
            debug_handler = RotatingFileHandler(debug_log_filename, maxBytes=self.MAX_LOG_FILE_SIZE,
                                                backupCount=self.BACKUP_COUNT)
            debug_handler.setLevel(logging.DEBUG)

            # Rotating info handler
            info_handler = RotatingFileHandler(info_log_filename, maxBytes=self.MAX_LOG_FILE_SIZE,
                                               backupCount=self.BACKUP_COUNT)
            info_handler.setLevel(logging.INFO)

            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)

            # Formatter
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            debug_handler.setFormatter(formatter)
            info_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # Attach handlers
            self.logger.addHandler(debug_handler)
            self.logger.addHandler(info_handler)
            self.logger.addHandler(console_handler)

    def log(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)

    def critical(self, message):
        self.logger.critical(message)

    def exception(self, message):
        self.logger.exception(message)

    def shutdown(self):
        logging.shutdown()
