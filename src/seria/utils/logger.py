import logging
import sys


class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Create console handler and set level to INFO
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Create formatter
        log_format = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
        formatter = logging.Formatter(log_format)

        # Add formatter to console handler
        ch.setFormatter(formatter)

        # Add console handler to logger
        self.logger.addHandler(ch)

    def get_logger(self):
        return self.logger


def decolor_discord_logging():
    """
    Set up a custom logging configuration for the discord.py library.
    
    This function configures a logger named "discord" to output logs at the
    INFO level or higher. The log output is directed to the console (stdout)
    without any color formatting. The log format includes a timestamp, log level,
    logger name, and the log message.
    """
    
    # Create a logger object
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)

    # Create a stream handler (console output)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # Create a log format without color codes
    log_format = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)