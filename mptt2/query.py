from typing import Any, Dict
from django.db.models.query_utils import Q
from django.db.models.expressions import F, OuterRef

class ConvertableQuery(Q):
    
    def to_subquery(self):
        for key, value in self.children:
            if "mptt_" in key:
                # TODO: convert F to OuterRef objects
                if isinstance(value.lhs, F):
                    pass
                elif isinstance (value.rhs, F):
                    pass

class ParentQuery(ConvertableQuery):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            mptt_lft=F("mptt_lft") - 1,
            mptt_rgt=F("mptt_rgt") + 1,
            tree_id=F("tree_id"),
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
        super().__init__(*args, **kwargs)
        self.__or__(
            other=AncestorsQuery(include_self=include_self)
        )


class ChildrenQuery(DescendantsQuery):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(mptt_depth=self.sub_expression_type("mptt_depth") + 1, *args, **kwargs)


class LeafNodesQuery(DescendantsQuery):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(mptt_lft=self.sub_expression_type("mptt_rgt") - 1, *args, **kwargs)


class DescendantCountQuery(ConvertableQuery): 
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            (F("mptt_rgt") - F("mptt_lft")) // 2,
            *args, 
            **kwargs
        )


# TODO:
# class TreeQuerySet(QuerySet):
    
#     def get_parent(self):
#         self.filter()