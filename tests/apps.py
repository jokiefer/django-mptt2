from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TestConfig(AppConfig):
    name = "tests"
    verbose_name = _("tests")
    default_auto_field = 'django.db.models.AutoField'
