import os
import logging
import datetime


def loggen():
    current_path = os.path.abspath(os.path.dirname(__file__))

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{current_path}\\Logs\\automation_{timestamp}.html"
    print(log_file)
    # Create a new HTMLFileHandler
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.INFO)

    # Define the HTML log format
    formatter = logging.Formatter(
        '<p>%(asctime)s: %(levelname)s: %(message)s</p>', datefmt='%m/%d/%Y %I:%M:%S %p')
    file_handler.setFormatter(formatter)

    # Create a new logger and add the HTMLFileHandler to it
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    return logger

loggen()