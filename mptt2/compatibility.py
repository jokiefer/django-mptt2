from django import VERSION
from django.utils.translation import gettext as _


def violation_error_message_kwargs():
    # adds backward compatibility
    major, minor, fix, state, x = VERSION
    if major == 4 and minor >= 1:
        return {
            "violation_error_message": _("The right side value rgt is allways greater than the node left side value lft.")
        }
    return {}
