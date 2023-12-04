import logging


class MyLogger:
    def __init__(self, log_filename, log_level=logging.INFO):
        self.log_filename = log_filename
        self.log_level = log_level

        logging.basicConfig(filename=self.log_filename, level=self.log_level, format="%(asctime)s - %(levelname)s - %(message)s")

    def log(self, message):
        logging.info(message)

    def error(self, message):
        logging.error(message)

    def warning(self, message):
        logging.warning(message)

    def critical(self, message):
        logging.critical(message)

    def exception(self, message):
        logging.exception(message)

    def shutdown(self):
        logging.shutdown()
