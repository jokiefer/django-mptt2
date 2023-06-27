from django.contrib.admin.options import ModelAdmin
from django.forms.fields import ChoiceField
from django.forms.models import ModelChoiceField, ModelForm
from django.http.request import HttpRequest
from django.urls.conf import path
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_protect

from mptt2.enums import Position


csrf_protect_m = method_decorator(csrf_protect)
from django.contrib.admin.decorators import display
from django.contrib.admin.widgets import AdminTextInputWidget
from django.urls import reverse
from django.utils.html import format_html, mark_safe


class InsertAtForm(ModelForm):


    def __init__(self, *args, **kwargs) -> None:
        
        super().__init__(*args, **kwargs)        
        # dynamic initial the queryset based on the current model class
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

    class Meta:
        fields = ["target", "position"]

    def save(self, *args, **kwargs):
        return self.move_to()

    def save_m2m(self):
        self._save_m2m()

    def move_to(self):
        if self.errors:
            raise ValueError(
                f"The {self.instance._meta.object_name} could not be moved because the data didn't validate."
            )
        moved_node = self.instance.move_to(self.cleaned_data["target"], self.cleaned_data["position"])
        self._save_m2m()
        return moved_node


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


    @display(description=_("Delete"))
    def delete_link(self, obj):
        if self.has_delete_permission(request=self.request, obj=obj):
            return format_html(f'<a class="deletelink" href="{reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete", args=(obj.id,))}">'f"{_('Delete')}"'</a>')

    @display(description=_("Move"))
    def move_link(self, obj):
        if self.has_change_permission(request=self.request, obj=obj):
            return format_html(f'<a href="{reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_move", args=(obj.id,))}">'f"&#8982; {_('Move')}"'</a>')


    def tree_node_string(self, obj):
        level_string = "".join("&nbsp;&nbsp;" for _ in range(obj.mptt_depth))
        return mark_safe(f"{level_string}&#x2022; {obj}")
   

    def get_actions(self, request: HttpRequest):
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
        
        list_display.append("delete_link")
        list_display.append("move_link")
        return list_display

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "insert_at/", 
                self.admin_site.admin_view(self.add_view), 
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_insert",
                kwargs={"extra_context": {"title": "Insert node"}}
            ),
            path(
                "<path:object_id>/move_to/", 
                self.admin_site.admin_view(self.change_view), 
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_move",
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

    def get_form(self, request, obj=None, change=False, **kwargs):
        if self.is_insert_at_action(request):
            # if request.method == "GET":
            fields = kwargs.pop("fields")
            if not fields:
                # django displays by default an empty form if the user has no change permission. Then fields is in kwargs with None value.
                # Hover, if this happens the follwing line will crash https://github.com/django/django/blob/cf79f92abee2ff5fd4fdcc1a124129a9773805b8/django/contrib/admin/options.py#L677
                # So just pass in __all__ fields, so all fields will be excluded. ¯\_(ツ)_/¯
                fields = '__all__'
            return super().get_form(request, obj, change, form=self.get_insert_at_form(), fields=fields, **kwargs)
        elif self.is_move_to_action(request):
            if request.method == "GET":
                fields = kwargs.pop("fields")
                if not fields:
                    # same as above
                    fields = '__all__'
                return super().get_form(request, obj, change, form=self.get_move_to_form(), fields=fields, **kwargs)
            return super().get_form(request, obj, change, form=self.get_move_to_form(), **kwargs)
        return super().get_form(request, obj, change, **kwargs)
    
    

    def changelist_view(self, request, extra_context=None):
        """Adds request attribute to this admin view"""
        self.request = request
        if not extra_context:
            extra_context = {}
        extra_context.update({"can_insert": True if self.has_add_permission(request) else False})
        
        return super().changelist_view(request, extra_context=extra_context)



class MPTTDraggableModelAdmin(MPTTModelAdmin):
    """
    A basic admin class that displays tree items according to their position in
    the tree.  No extra editing functionality beyond what Django admin normally
    offers.
    """
    change_list_template = "admin/mptt_draggable_change_list.html"
