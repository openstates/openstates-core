import os
import django
from django import conf
import dj_database_url


def init_django():  # pragma: no cover
    DATABASE_URL = os.environ.get(
        "DATABASE_URL", "postgis://openstates:openstates@localhost/openstates"
    )
    DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}

    conf.settings.configure(
        conf.global_settings,
        SECRET_KEY="not-important",
        DEBUG=False,
        INSTALLED_APPS=(
            "django.contrib.contenttypes",
            "openstates.data",
            "openstates.reports",
        ),
        DATABASES=DATABASES,
        MIDDLEWARE_CLASSES=(),
    )
    django.setup()
