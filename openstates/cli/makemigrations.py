# type: ignore
from ..utils.django import init_django
from django.core import management


def main() -> None:
    init_django()
    management.call_command("makemigrations")
