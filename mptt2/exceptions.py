class InvalidMove(Exception):
    """An invalid node move was attempted.
    For example, attempting to make a node a child of itself.
    """

    pass


class InvalidInsert(Exception):
    """An invalid node insert was attempted.
    For example, attempted to make a node a sibling of the root node.
    """
    pass
