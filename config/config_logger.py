# Global logger instance
# Usage: logger = setup_logging()
import os
import logging
from colorama import Fore, Style, init

init(autoreset=True)

ENV = os.getenv('APP_ENV', 'development')

LOG_CONFIG = {
    'development': {
        'log_level': logging.DEBUG,
        'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'log_to_console': True,
        'use_colors': True,
    },
    'production': {
        'log_level': logging.INFO,
        'log_format': '%(name)s - %(levelname)s - %(message)s',
        'log_to_console': True,
        'use_colors': False,
    }
}

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def __init__(self, fmt, use_colors=True):
        super().__init__(fmt)
        self.use_colors = use_colors

    def format(self, record):
        if self.use_colors:
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
                record.msg = f"{self.COLORS[levelname]}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

def setup_logging():
    config = LOG_CONFIG.get(ENV, LOG_CONFIG['development'])
    
    logger = logging.getLogger('yesterdays-wisdom')
    logger.setLevel(config['log_level'])
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    if config['log_to_console']:
        console_handler = logging.StreamHandler()
        colored_formatter = ColoredFormatter(config['log_format'], use_colors=config['use_colors'])
        console_handler.setFormatter(colored_formatter)
        logger.addHandler(console_handler)
    
    # No propagation to avoid duplicate logs
    logger.propagate = False

    return logger

logger = setup_logging()
