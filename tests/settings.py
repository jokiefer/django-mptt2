import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INSTALLED_APPS = [
    "mptt2",
    "tests"
]

DATABASES = { "default": {'ENGINE': 'django.db.backends.sqlite3',  'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),}}

