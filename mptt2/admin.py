
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple, Union

from django.contrib.admin.options import ModelAdmin
from django.core.exceptions import PermissionDenied
from django.db import models, router, transaction
from django.forms.fields import ChoiceField
from django.forms.models import ModelChoiceField, ModelForm, modelform_factory
from django.http.request import HttpRequest
from django.template.response import TemplateResponse
from django.urls.conf import path
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect

from mptt2.enums import Position
from mptt2.exceptions import MethodNotAllowed

csrf_protect_m = method_decorator(csrf_protect)
from django.contrib.admin.decorators import display
from django.contrib.admin.sites import site
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.admin.widgets import AdminTextInputWidget
from django.urls import reverse
from django.utils.html import format_html
from django.views.generic.edit import FormView


class InsertAtForm(ModelForm):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["target"].queryset = self.instance.__class__.objects.all()

    target = ModelChoiceField(
        queryset=None, 
        required=False, 
        help_text=_("leave empty if you wan't to create a new root node"),
        widget=AdminTextInputWidget
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
    

class MoveToForm(ModelForm):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["target"].queryset = self.instance.__class__.objects.all()

    target = ModelChoiceField(
        queryset=None, 
        help_text=_("leave empty if you wan't to create a new root node"),
        widget=AdminTextInputWidget
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
                f"The {self.instance._meta.object_name} could not be moved because the data didn't validate."
            )
        new_obj = self.instance.move_to(self.cleaned_data["target"], self.cleaned_data["position"])
        self._save_m2m()
        return new_obj


class MPTTModelAdmin(ModelAdmin):
    """
    A basic admin class that displays tree items according to their position in
    the tree.  No extra editing functionality beyond what Django admin normally
    offers.
    """
    change_list_template = "admin/mptt_change_list.html"
    search_fields = ["pk"]
    insert_at_form = InsertAtForm
    move_to_form = MoveToForm

    @display(description=_("Move"))
    def move_node(self, obj):
        if self.has_change_permission(request=self.request, obj=obj):
            return format_html(
                f'<span data-id="{obj.id}" data-lft="{obj.mptt_lft}" data-rgt="{obj.mptt_rgt}" data-depth="{obj.mptt_depth}" data-has-leafs="{str(obj.has_leafs).lower()}" data-depth="{obj.mptt_depth}" class="mdi mdi-cursor-move"></span>'
            )

    @display(description=_("Insert"))
    def insert_links(self, obj):
        return format_html(
            '<div class="submit-row">'
            f'<a class="button" href="{reverse("admin:node-insert")}?target={obj.pk}&position=last-child">Last Child</a>'
            f'<a class="button" href="{reverse("admin:node-insert")}?target={obj.pk}&position=first-child">First Child</a>'
            f'<a class="button" href="{reverse("admin:node-insert")}?target={obj.pk}&position=left">Left</a>'
            f'<a class="button" href="{reverse("admin:node-insert")}?target={obj.pk}&position=right">Right</a>'
            '</div>'
        )

    @display(description=_("Delete"))
    def delete_link(self, obj):
        if self.has_delete_permission(request=self.request, obj=obj):
            return format_html(f'<a class="button" href="{reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete", args=(obj.id,))}">Delete</a>')


    def tree_node_string(self, obj):
        level_string = "".join("-" for _ in range(obj.mptt_depth))
        return f"{level_string} {obj}"
   

    def get_actions(self, request: HttpRequest) -> OrderedDict[Any, Any]:
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            # queryset.delete() is not implemented for now.
            del actions["delete_selected"]
        return actions

    def get_list_display(self, request):
        """
        Return a sequence containing the fields to be displayed on the
        changelist.
        """
        list_display = list(super().get_list_display(request))
        if "__str__" in list_display:
            list_display[list_display.index("__str__")] = self.tree_node_string
        
        if self.has_add_permission(request=request):
            list_display.append("insert_links")

        list_display.insert(1, "move_node")
        list_display.append("delete_link")
        return list_display

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "insert_at/", 
                self.admin_site.admin_view(self.add_view), 
                name="node-insert",
                kwargs={"extra_context": {"title": "Insert node"}}
            ),
            path(
                "move_to/", 
                self.admin_site.admin_view(self.change_view), 
                name="node-move",
                kwargs={"extra_context": {"title": "Move node"}}
            )
        ]
        return my_urls + urls

    def get_insert_at_form(self):
        return self.insert_at_form

    def get_move_to_form(self):
        return self.move_to_form

    def is_insert_at_action(self, request):
        return "insert_at" in request.path

    def is_move_to_action(self, request):
        return "move_to" in request.path

    def get_form(self, request: Any, obj: Any | None = ..., change: bool = ..., **kwargs: Any) -> Any:
        if self.is_insert_at_action(request):
            return super().get_form(request, obj, change, form=self.get_insert_at_form(), **kwargs)
        elif self.is_move_to_action(request):
            return super().get_form(request, obj, change, form=self.get_move_to_form(), **kwargs)
        return super().get_form(request, obj, change, **kwargs)

    def changelist_view(self, request, extra_context=None):
        """Adds request attribute to this admin view"""
        self.request = request
        return super().changelist_view(request, extra_context=extra_context)
    