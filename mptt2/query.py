from typing import Any, Dict
from django.db.models.query_utils import Q
from django.db.models.expressions import F, OuterRef, CombinedExpression
from django.db.models.query import QuerySet


class ConvertableQuery(Q):
    
    def convert_field_ref_expression(self, children, key, value):
        if isinstance(value, CombinedExpression):
            # TODO: convert F to OuterRef objects
            if isinstance(value.lhs, F):
                value.lhs = OuterRef(value.lhs.name)
            elif isinstance (value.rhs, F):
                value.rhs = OuterRef(value.rhs.name)
        else:
            index = children.index((key, value))
            children[index] = (key, OuterRef(value.name))

    def to_subquery(self):
        """To use this query inside a subquery, this function converts the current query with F object references to OuterRef references."""
        for child in self.children:
            if isinstance(child, tuple):
                key, value = child
                self.convert_field_ref_expression(children=self.children, key=key, value=value)
            else:
                # we've got a list of Q nodes; so we need to call the to_subquery() of the Custom Q node to convert them.
                if hasattr(child, "to_subquery"):
                    child.to_subquery()

class ParentQuery(ConvertableQuery):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            mptt_lft=F("mptt_lft") - 1,
            mptt_rgt=F("mptt_rgt") + 1,
            mptt_tree_id=F("mptt_tree_id"),
            *args, 
            **kwargs
        )

class DescendantsQuery(ConvertableQuery):
    def __init__(self, include_self: bool = False, *args: Any, **kwargs: Any) -> None:
        query_kwargs: Dict = {
            "mptt_lft_lte" if include_self else "mptt_lft_lt": F("mptt_lft"),
            "mptt_rgt_gte" if include_self else "mptt_rgt_gt": F("mptt_rgt"),
            "mptt_tree_id": F("mptt_tree_id")
        }
        super().__init__(
            *args, 
            **kwargs,
            **query_kwargs
        )


class AncestorsQuery(ConvertableQuery):
    def __init__(self, include_self: bool = False, *args: Any, **kwargs: Any) -> None:
        query_kwargs: Dict = {
        "mptt_lft_gte" if include_self else "mptt_lft_gt": F("mptt_lft"),
        "mptt_rgt_lte" if include_self else "mptt_rgt_lt": F("mptt_rgt"),
        "mptt_tree_id": F("mptt_tree_id")
    }
        super().__init__(
            *args, 
            **kwargs, 
            **query_kwargs
        )




class FamilyQuery(DescendantsQuery):
    def __init__(self, include_self: bool = False, *args: Any, **kwargs: Any) -> None:
        super().__init__(include_self=include_self, *args, **kwargs)
        self.add(data=AncestorsQuery(include_self=include_self), conn_type=self.OR)
        


class ChildrenQuery(DescendantsQuery):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(mptt_depth=F("mptt_depth") + 1, *args, **kwargs)


class LeafNodesQuery(DescendantsQuery):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(mptt_lft=F("mptt_rgt") - 1, *args, **kwargs)



class TreeQuerySet(QuerySet):
    
    def with_descendant_count(self):
        self.annotate(descendant_count=F("mptt_rgt") - F("mptt_lft") // 2)

    