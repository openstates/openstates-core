import os
from .utils import transformers

# scrape settings

SCRAPELIB_RPM = 60
SCRAPELIB_TIMEOUT = 60
SCRAPELIB_RETRY_ATTEMPTS = 3
SCRAPELIB_RETRY_WAIT_SECONDS = 10
SCRAPELIB_VERIFY = True

CACHE_DIR = os.path.join(os.getcwd(), "_cache")
SCRAPED_DATA_DIR = os.path.join(os.getcwd(), "_data")

# import settings

ENABLE_BILLS = True
ENABLE_VOTES = True
ENABLE_PEOPLE_AND_ORGS = False
ENABLE_EVENTS = False

IMPORT_TRANSFORMERS = {"bill": {"identifier": transformers.fix_bill_id}}

# Django settings
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s %(name)s: %(message)s",
            "datefmt": "%H:%M:%S",
        }
    },
    "handlers": {
        "default": {
            "level": "DEBUG",
            "class": "openstates.utils.ansistrm.ColorizingStreamHandler",
            "formatter": "standard",
        }
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "DEBUG", "propagate": True},
        "scrapelib": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "requests": {"handlers": ["default"], "level": "WARN", "propagate": False},
        "boto": {"handlers": ["default"], "level": "WARN", "propagate": False},
    },
}
