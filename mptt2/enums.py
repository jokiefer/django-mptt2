from typing import Tuple

from django.db.models.enums import TextChoices
from django.utils.translation import gettext_lazy as _


class Position(TextChoices):
    """Simple enum to provide pre defined position choices"""

    LAST_CHILD: Tuple[str, str] = "last-child", _("Last Child")
    """the node shall be the rightmost child of the target"""

    FIRST_CHILD: Tuple[str, str] = "first-child", _("First Child")
    """the node shall be the leftmost child of the target"""

    LEFT: Tuple[str, str] = "left", _("Left")
    """the node shall be the left sibling of the target"""

    RIGHT: Tuple[str, str] = "right", _("Right")
    """the node shall be the right sibling of the target"""


