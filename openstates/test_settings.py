import os

# django settings for tests
SECRET_KEY = "test"
INSTALLED_APPS = (
    "django.contrib.contenttypes",
    "openstates.data",
    "openstates.reports",
)
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": "test",
        "USER": "test",
        "PASSWORD": "test",
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
    }
}
MIDDLEWARE_CLASSES = ()
