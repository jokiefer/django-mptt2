from django.contrib import admin
from django.contrib.admin.options import ModelAdmin

from mptt2.admin import MPTTDraggableModelAdmin, MPTTModelAdmin
from mptt2.models import Tree
from tests.models import OtherNode, SimpleNode


admin.site.register(Tree, ModelAdmin)
admin.site.register(SimpleNode, MPTTDraggableModelAdmin)

admin.site.register(OtherNode, MPTTModelAdmin)

