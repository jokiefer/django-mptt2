
from typing import Any

from django.contrib.admin.options import ModelAdmin
from django.core.exceptions import PermissionDenied
from django.db import models, router, transaction
from django.forms.fields import ChoiceField
from django.forms.models import ModelChoiceField, ModelForm, modelform_factory
from django.urls.conf import path
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect

from mptt2.enums import Position
from mptt2.exceptions import MethodNotAllowed

csrf_protect_m = method_decorator(csrf_protect)
from django.contrib.admin.decorators import display
from django.contrib.admin.utils import flatten_fieldsets
from django.views.generic.edit import FormView


class InsertAtForm(ModelForm):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["target"].queryset = self.instance.__class__.objects.all()

    target = ModelChoiceField(
        queryset=None, 
        required=False, 
        help_text=_("leave empty if you wan't to create a new root node")
    )
    position= ChoiceField(
        choices=Position.choices,
        initial=Position.LAST_CHILD, 
        required=False
        )

    def save(self, *args, **kwargs):
        return self.insert_at()

    def save_m2m(self):
        self._save_m2m()

    def insert_at(self):
        if self.errors:
            raise ValueError(
                f"The {self.instance._meta.object_name} could not be inserted because the data didn't validate."
            )
        new_obj = self.instance.insert_at(self.cleaned_data["target"], self.cleaned_data["position"])
        self._save_m2m()
        return new_obj



@display()
def tree_node(obj):
    level_string = "".join("-" for _ in range(obj.mptt_depth))
    return f"{level_string} {obj}"

class MPTTModelAdmin(ModelAdmin):
    """
    A basic admin class that displays tree items according to their position in
    the tree.  No extra editing functionality beyond what Django admin normally
    offers.
    """
    list_display = [tree_node]
    change_list_template = "admin/mptt_change_list.html"
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("insert_at/", self.admin_site.admin_view(self.add_view), kwargs={"extra_context": {"title": "Insert node"}})]
        return my_urls + urls

    def is_insert_at_action(self, request):
        return "insert_at" in request.path

    def get_form(self, request: Any, obj: Any | None = ..., change: bool = ..., **kwargs: Any) -> Any:
        if self.is_insert_at_action(request):
            return super().get_form(request, obj, change, form=InsertAtForm, **kwargs)
        return super().get_form(request, obj, change, **kwargs)
