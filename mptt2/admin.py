
from typing import Any, Dict, Mapping, Optional, Type, Union

from django.contrib.admin.options import ModelAdmin
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.fields import ChoiceField
from django.forms.models import ModelChoiceField, ModelForm, modelform_factory
from django.forms.utils import ErrorList
from django.urls.conf import path

from mptt2.enums import Position
from mptt2.utils import enum_as_choices


class InsertAtForm(ModelForm):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["target"].queryset = self.instance.__class__.objects.all()

    # TODO: translate help_text
    target = ModelChoiceField(queryset=None, required=False, help_text="leave empty if you wan't to create a new root node")
    position= ChoiceField(choices=enum_as_choices(Position))

    def save(self, commit: bool = ...) -> Any:
        if self.errors:
            raise ValueError(
                f"The {self.instance._meta.object_name} could not be inserted because the data didn't validate."
            )
        return self.instance.insert_at(**self.cleaned_data)


class MPTTModelAdmin(ModelAdmin):
    """
    A basic admin class that displays tree items according to their position in
    the tree.  No extra editing functionality beyond what Django admin normally
    offers.
    """
    change_list_template = "admin/mptt_change_list.html"
    
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path("insert_at/", self.admin_site.admin_view(self.add_view), kwargs={"extra_context": {"title": "Insert node"}})]
        return my_urls + urls


    def is_insert_at_action(self, request):
        return "insert_at" in request.path

    def get_form(self, request: Any, obj: Any | None = ..., change: bool = ..., **kwargs: Any) -> Any:
        if self.is_insert_at_action(request):
            return modelform_factory(self.model, form=InsertAtForm, fields="__all__")
        return super().get_form(request, obj, change, **kwargs)

    # def save_form(self, request: Any, form: Any, change: Any) -> Any:
    #     if self.is_insert_at_action(request):
    #         return form.instance.insert_at()
    #     return super().save_form(request, form, change)
