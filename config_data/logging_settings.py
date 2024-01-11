import sys

from filters.log_filters import DebugWarningLogFilter, CriticalLogFilter, ErrorLogFilter, InfoFileLogFilter


logging_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '#%(levelname)-8s %(name)s:%(funcName)s - %(message)s'
        },
        'formatter_stderr': {
            'format': '[%(asctime)s] #%(levelname)-8s %(filename)s:'
                      '%(lineno)d - %(name)s:%(funcName)s - %(message)s'
        },
        'formatter_2': {
            'format': '#%(levelname)-8s [%(asctime)s] - %(filename)s:'
                      '%(lineno)d - %(name)s:%(funcName)s - %(message)s'
        },
        'formatter_file': {
            'format': '[%(asctime)s] - %(message)s'
        }
    },
    'filters': {
        'critical_filter': {
            '()': CriticalLogFilter,
        },
        'error_filter': {
            '()': ErrorLogFilter,
        },
        'debug_warning_filter': {
            '()': DebugWarningLogFilter,
        },
        'info_file_filter': {
            '()': InfoFileLogFilter,
        }
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'default'
        },
        'stderr': {
            'class': 'logging.StreamHandler',
            'formatter': 'formatter_stderr'
        },
        'stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'formatter_2',
            'stream': sys.stdout
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'filename': 'error.log',
            'mode': 'w',
            'level': 'DEBUG',
            'formatter': 'formatter_stderr',
            'filters': ['error_filter']
        },
        'critical_file': {
            'class': 'logging.FileHandler',
            'filename': 'critical.log',
            'mode': 'w',
            'formatter': 'formatter_file',
            'filters': ['critical_filter']
        },
        'info_file': {
            'class': 'logging.FileHandler',
            'filename': 'user.log',
            'mode': 'a',
            'formatter': 'formatter_file',
            'filters': ['info_file_filter']
        }
    },
    'loggers': {
        'bot': {
            'level': 'DEBUG',
            'handlers': ['stderr']
        },
        'handlers.user_handlers': {
            'level': 'INFO',
            'handlers': ['info_file', 'stderr']
        }
    },
    'root': {
        'formatter': 'default',
        'handlers': ['default']
    }
}