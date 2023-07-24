import logging
import time


def log_error(message):
    logging.basicConfig(filename='error.log', level=logging.ERROR)
    logging.error(message, exc_info=True)


def log_info(command_name):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    log_message = f"{timestamp}:{command_name}"
    logging.basicConfig(filename='info.log', level=logging.INFO)
    logging.info(log_message)
