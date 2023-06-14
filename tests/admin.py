from django.contrib import admin

from mptt2.admin import MPTTModelAdmin
from tests.models import SimpleNode

admin.site.register(SimpleNode, MPTTModelAdmin)
