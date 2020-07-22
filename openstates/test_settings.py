import os
import dj_database_url

# django settings for tests
SECRET_KEY = "test"
INSTALLED_APPS = (
    "django.contrib.contenttypes",
    "openstates.data",
    "openstates.reports",
)
MIDDLEWARE_CLASSES = ()
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "test",
        "USER": "test",
        "PASSWORD": "test",
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
    }
}
DATABASE_URL = os.environ.get("OVERRIDE_DATABASE_URL")
if DATABASE_URL:
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
