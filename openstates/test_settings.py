import os
import dj_database_url  # type: ignore

# django settings for tests
SECRET_KEY = "test"
INSTALLED_APPS = (
    "django.contrib.contenttypes",
    "openstates.data",
)
MIDDLEWARE_CLASSES = ()
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test",
        "USER": "test",
        "PASSWORD": "test",
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
    }
}
TIME_ZONE = "UTC"
DATABASE_URL = os.environ.get("OVERRIDE_DATABASE_URL")
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
