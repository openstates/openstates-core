import os
from .utils import transformers

# settings for realtime flag
S3_REALTIME_BASE = os.environ.get("S3_REALTIME_BASE")  # e.g 's3://realtime-bucket'
SQS_QUEUE_URL = os.environ.get(
    "SQS_QUEUE_URL"
)

# scrape settings

SCRAPELIB_RPM = 60
SCRAPELIB_TIMEOUT = 60
SCRAPELIB_RETRY_ATTEMPTS = 3
SCRAPELIB_RETRY_WAIT_SECONDS = 10
try:
    verify = os.environ.get("VERIFY_CERTS", False)
    if verify == "False":
        verify = False
except Exception:
    verify = False
SCRAPELIB_VERIFY = verify

CACHE_DIR = os.path.join(os.getcwd(), "_cache")
SCRAPED_DATA_DIR = os.path.join(os.getcwd(), "_data")

IMPORT_TRANSFORMERS = {
    "bill": {
        "identifier": transformers.fix_bill_id,
        "documents": {"note": transformers.truncate_300},  # TODO remove when db migration done
        "versions": {"note": transformers.truncate_300},  # TODO remove when db migration done
    },
    "event": {
        "media": {"note": transformers.truncate_300},  # TODO remove when db migration done
    }
}

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
