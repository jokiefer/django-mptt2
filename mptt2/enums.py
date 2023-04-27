from enum import Enum


class Position(Enum):
    """Simple enum to provide pre defined position choices"""
    LAST_CHILD: str = "last-child"
    FIRST_CHILD: str = "first-child"
    LEFT: str = "left"
    RIGHT: str = "right"
