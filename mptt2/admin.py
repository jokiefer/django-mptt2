from django.contrib.admin.options import ModelAdmin


class MPTTModelAdmin(ModelAdmin):
    """
    A basic admin class that displays tree items according to their position in
    the tree.  No extra editing functionality beyond what Django admin normally
    offers.
    """
    change_list_template = "admin/mptt_change_list.html"
