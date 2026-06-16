"""
Settings used when running the test suite — in-memory SQLite so
tests run fast and never touch db.sqlite3 used by dev.
"""
from .base import *  # noqa: F401, F403

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
