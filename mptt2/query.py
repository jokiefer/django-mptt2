from typing import Dict
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.db.models.expressions import F, OuterRef


def get_expression(subquery: bool = False) -> OuterRef | F:
    return OuterRef if subquery else F


def get_parent_query(subquery: bool = False) -> Q:
    expression = get_expression(subquery)
    return Q(
        mptt_lft=expression("mptt_lft") - 1,
        mptt_rgt=expression("mptt_rgt") + 1,
        tree_id=expression("tree_id")
    )


def get_descendants_query(include_self: bool = False, subquery: bool = False) -> Q:
    expression = get_expression(subquery)
    query_kwargs: Dict = {
        "mptt_lft_lte" if include_self else "mptt_lft_lt": expression("mptt_lft"),
        "mptt_rgt_gte" if include_self else "mptt_rgt_gt": expression("mptt_rgt"),
        "tree_id": expression("tree_id")
    }
    return Q(**query_kwargs)


def get_ancestors_query(include_self: bool = False, subquery: bool = False) -> Q:
    expression = get_expression(subquery)
    query_kwargs: Dict = {
        "mptt_lft_gte" if include_self else "mptt_lft_gt": expression("mptt_lft"),
        "mptt_rgt_lte" if include_self else "mptt_rgt_lt": expression("mptt_rgt"),
        "tree_id": expression("tree_id")
    }
    return Q(**query_kwargs)


def get_family_query(subquery: bool = False) -> Q:
    return get_descendants_query(True, subquery) | get_ancestors_query(True, subquery)


def get_children_query(subquery: bool = False) -> Q:
    expression = get_expression(subquery)
    return get_descendants_query(subquery) & Q(mptt_depth=expression("mptt_depth") + 1)


def get_leaf_nodes_query(include_self: bool = False, subquery: bool = False) -> Q:
    expression = get_expression(subquery)
    return get_descendants_query(include_self, subquery) & Q(mptt_lft=expression("mptt_right") - 1)


def get_descendant_count_query(subquery: bool = False) -> Q:
    expression = get_expression(subquery)
    return Q(expression("mptt_rgt") - expression("mptt_lft") // 2)


class TreeQuerySet(QuerySet):
    
    def get_parent(self):
        self.filter()