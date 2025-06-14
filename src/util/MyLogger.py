import logging


class MyLogger:
    def __init__(self, name, debug_log_filename='logs/debug.log', info_log_filename='logs/info.log'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Set the logger to the lowest level to capture all messages

        # Create handlers
        debug_handler = logging.FileHandler(debug_log_filename)
        debug_handler.setLevel(logging.DEBUG)

        info_handler = logging.FileHandler(info_log_filename)
        info_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Add formatter to handlers
        debug_handler.setFormatter(formatter)
        info_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.logger.addHandler(debug_handler)
        self.logger.addHandler(info_handler)

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
