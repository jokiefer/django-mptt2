from django.db.models import F


class Left(F):
    """Shortcut for mptt_lft field expression"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(name="mptt_lft", *args,  **kwargs)


class Right(F):
    """Shortcut for mptt_rgt field expression"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(name="mptt_rgt", *args,  **kwargs)
