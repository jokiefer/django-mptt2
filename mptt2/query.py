from typing import Any, Dict

from django.db.models.expressions import CombinedExpression, F, OuterRef
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q


class ConvertableQuery(Q):

    def convert_field_ref_expression(self, children, key, value):
        if isinstance(value, CombinedExpression):
            if isinstance(value.lhs, F):
                value.lhs = OuterRef(value.lhs.name)
            elif isinstance(value.rhs, F):
                value.rhs = OuterRef(value.rhs.name)
        else:
            index = children.index((key, value))
            children[index] = (key, OuterRef(value.name))

    def to_subquery(self):
        """To use this query inside a subquery, this function converts the current query with F object references to OuterRef references."""
        for child in self.children:
            if isinstance(child, tuple):
                key, value = child
                self.convert_field_ref_expression(
                    children=self.children, key=key, value=value)
            else:
                # we've got a list of Q nodes; so we need to call the to_subquery() of the Custom Q node to convert them.
                if hasattr(child, "to_subquery"):
                    child.to_subquery()


class SameTreeQuery(ConvertableQuery):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if "mptt_tree" in kwargs:
            super().__init__(*args, **kwargs)
        else:
            # FIXME: does not take any effect, a concrete tree object (pk) is needed to filter it correctly
            super().__init__(mptt_tree=F("mptt_tree"), *args, **kwargs)


class RootQuery(SameTreeQuery):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            mptt_parent=None,
            *args,
            **kwargs
        )


class ParentQuery(SameTreeQuery):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            mptt_lft=F("mptt_lft") - 1,
            mptt_rgt=F("mptt_rgt") + 1,
            *args,
            **kwargs
        )


class DescendantsQuery(SameTreeQuery):
    def __init__(self, of=None, include_self: bool = False, *args: Any, **kwargs: Any) -> None:
        query_kwargs: Dict = {
            "mptt_lft__gte" if include_self else "mptt_lft__gt": of.mptt_lft if of else F("mptt_lft"),
            "mptt_rgt__lte" if include_self else "mptt_rgt__lt": of.mptt_rgt if of else F("mptt_rgt"),
        }
        if of:
            query_kwargs.update({"mptt_tree": of.mptt_tree})
        super().__init__(
            *args,
            **kwargs,
            **query_kwargs
        )


class AncestorsQuery(SameTreeQuery):
    def __init__(self, of=None, include_self: bool = False, *args: Any, **kwargs: Any) -> None:
        query_kwargs: Dict = {
            "mptt_lft__lte" if include_self else "mptt_lft__lt": of.mptt_lft if of else F("mptt_lft"),
            "mptt_rgt__gte" if include_self else "mptt_rgt__gt": of.mptt_rgt if of else F("mptt_rgt"),
        }
        if of:
            query_kwargs.update({"mptt_tree": of.mptt_tree})
        super().__init__(
            *args,
            **kwargs,
            **query_kwargs
        )


class FamilyQuery(DescendantsQuery):
    def __init__(self, include_self: bool = False, *args: Any, **kwargs: Any) -> None:
        super().__init__(include_self=include_self, *args, **kwargs)
        self.add(data=AncestorsQuery(
            include_self=include_self), conn_type=self.OR)


class ChildrenQuery(DescendantsQuery):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(mptt_depth=F("mptt_depth") + 1, *args, **kwargs)


class SiblingsQuery(ConvertableQuery):
    def __init__(self, of=None, include_self: bool = False, *args: Any, **kwargs: Any) -> None:
        super().__init__(parent=of.parent if of else F("parent"), *args, **kwargs)
        if not include_self:
            self.add(data=~ConvertableQuery(pk=F("pk")), conn_type=self.AND)


class LeafNodesQuery(DescendantsQuery):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(mptt_lft=F("mptt_rgt") - 1, *args, **kwargs)


class TreeQuerySet(QuerySet):

    def with_descendant_count(self):
        self.annotate(descendant_count=F("mptt_rgt") - F("mptt_lft") // 2)
