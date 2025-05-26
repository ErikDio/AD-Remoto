import logging
import os
import sys

class Log_Handler:
    def __init__(self, log_name='ad_service'):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        log_path = os.path.join(base_path, f'{log_name}.log')

        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.FileHandler(log_path, encoding='utf-8')
            formatter = logging.Formatter('[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def write(self, message):
        self.logger.info(message)
