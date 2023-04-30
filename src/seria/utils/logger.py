import logging
import sys

class DiscordLogger:
    def __init__(self, name="discord", level=logging.INFO):
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
        """Add a custom stream handler to the logger without color formatting."""
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(self.level)
        log_format = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
