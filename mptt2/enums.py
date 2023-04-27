from enum import Enum


class Position(Enum):
    """Simple enum to provide pre defined position choices"""

    LAST_CHILD: str = "last-child"
    """the node shall be the rightmost child of the target"""

    FIRST_CHILD: str = "first-child"
    """the node shall be the leftmost child of the target"""

    LEFT: str = "left"
    """the node shall be the left sibling of the target"""

    RIGHT: str = "right"
    """the node shall be the right sibling of the target"""
