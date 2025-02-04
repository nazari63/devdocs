import logging
import logging.config
import sys

DEFAULT_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s [%(levelname)s] (%(name)s) %(message)s'
        },
    },
    'handlers': {
        'stderr': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': sys.stderr,
        },
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['stderr'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)


def get_logger(name) -> logging.Logger:
    return logging.getLogger(name)
