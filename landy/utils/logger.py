import sys
import time
import logging
import asyncio
from functools import wraps


class CustomLogger:
    """
    CustomLogger is a class for setting up a custom logger with the specified
    name and level.

    Usage:
        logger = CustomLogger("my_custom_logger")
        logger.info("This is an info message.")
        logger.warning("This is a warning message.")
        logger.error("This is an error message.")
    """

    def __init__(self, name, level=logging.INFO):
        """
        Initialize a CustomLogger instance.

        :param name: The name of the logger. Defaults to "my_custom_logger".
        :param level: The minimum log level to display. Defaults to
                      logging.INFO.
        """
        self.name = name
        self.level = level
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.level)
        self._remove_existing_handlers()
        self.handler = self._add_custom_handler()

    def _remove_existing_handlers(self):
        """Remove any existing handlers attached to the logger."""
        self.logger.handlers = []

    def _add_custom_handler(self):
        """Add a custom stream handler to the logger."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self.level)
        log_format = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def info(self, msg):
        """Log an info message."""
        self.logger.info(msg)

    def warning(self, msg):
        """Log a warning message."""
        self.logger.warning(msg)

    def error(self, msg):
        """Log an error message."""
        self.logger.error(msg)

    def debug(self, msg):
        """Log a debug message."""
        self.logger.debug(msg)

    def critical(self, msg):
        """Log a critical message."""
        self.logger.critical(msg)

    def log_execution_time(self, func):
        """
        Decorator that logs the execution time of the given function.

        :param func: The function whose execution time needs to be logged.
        :return: A wrapped function that logs the execution time.

        Example usage:
            logger = CustomLogger()

            @logger.log_execution_time
            async def example_async_function():
                await asyncio.sleep(1)

            @logger.log_execution_time
            def example_function():
                time.sleep(1)

        """
        @wraps(func)
        async def wrapper_async(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            self.info(f"{func.__name__} executed in {elapsed_time:.2f} secs.")
            return result

        def wrapper_sync(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            self.info(f"{func.__name__} executed in {elapsed_time:.2f} secs.")
            return result

        if asyncio.iscoroutinefunction(func):
            return wrapper_async
        else:
            return wrapper_sync

if __name__ == '__main__':
    logger = CustomLogger('seria_bot')
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
