# -*- coding: utf-8 -*-
import logging.config


LOG_SETTINGS = {
    'version': 1,
    'root': {
        'level': 'INFO',
        'handlers': ['console'],
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple'
        },
    },
    'formatters': {
        'simple': {
            'format': '%(levelname)s: %(module)s:%(lineno)s. %(message)s',
        },
    },
}

try:
    from local_logconfig import configure
except ImportError:
    def configure():
        logging.config.dictConfig(LOG_SETTINGS)
