from typing import Dict

from django.db.models import Case, Q, Value, When
from django.db.models.fields import PositiveIntegerField
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.db.transaction import atomic
from django.utils.translation import gettext as _

from mptt2.enums import Position
from mptt2.exceptions import InvalidMove
from mptt2.expressions import Depth, Left, Right
from mptt2.query import (DescendantsQuery, IsDescendantOfQuery,
                         RightSiblingsWithDescendants, RootQuery,
                         SameNodeQuery, TreeQuerySet)


class TreeManager(Manager):

    def get_queryset(self) -> QuerySet[TreeQuerySet]:
        return TreeQuerySet(self.model, using=self._db)

    def _calculate_node_mptt_values_for_insert(self, node, target, position):
        node.mptt_tree = target.mptt_tree
        if position == Position.LAST_CHILD:
            node.mptt_parent = target
            node.mptt_depth = target.mptt_depth + 1
            node.mptt_lft = target.mptt_rgt
            node.mptt_rgt = target.mptt_rgt + 1
        elif position == Position.FIRST_CHILD:
            node.mptt_parent = target
            node.mptt_depth = target.mptt_depth + 1
            node.mptt_lft = target.mptt_lft + 1
            node.mptt_rgt = target.mptt_lft + 2
        elif position == Position.LEFT:
            node.mptt_parent = target.mptt_parent
            node.mptt_depth = target.mptt_depth
            node.mptt_lft = target.mptt_lft
            node.mptt_rgt = target.mptt_lft + 1
        elif position == Position.RIGHT:
            node.mptt_parent = target.mptt_parent
            node.mptt_depth = target.mptt_depth
            node.mptt_lft = target.mptt_rgt + 1
            node.mptt_rgt = target.mptt_rgt + 2

    def _calculate_filter_for_insert(self, target, position):
        if position in [Position.LAST_CHILD, Position.RIGHT]:
            return (
                RootQuery(of=target) |
                RightSiblingsWithDescendants(
                    of=target, include_self=True if position == Position.LAST_CHILD else False)
            )
        else:
            return (
                RootQuery(of=target) |
                DescendantsQuery(of=target, include_self=True) |
                RightSiblingsWithDescendants(of=target)
            )

    def _calculate_conditional_update_for_insert(self, target, position) -> Dict:
        condition = ~RootQuery(of=target)

        if position in [Position.LAST_CHILD, Position.FIRST_CHILD]:
            condition &= ~SameNodeQuery(of=target)

        return {
            "mptt_lft": Case(
                When(
                    condition=condition,
                    then=Left() + 2
                ),
                default=Left(),
                output_field=PositiveIntegerField()
            ),
            "mptt_rgt": Right() + 2
        }

    @atomic
    def insert_node(self,
                    node,
                    target=None,
                    position: Position = Position.LAST_CHILD):
        """Tree function to insert this node to a given target relative by the given position

        :param target: The target node where the given node shall be inserted relative to.
        :type target: :class:`mptt2.models.Node`

        :param position: The relative position to the target
                         (Default: ``Position.LAST_CHILD``)
        :type target: :class:`mptt2.enums.Position`, optional

        :returns: the inserted node it self
        :rtype: :class:`mptt2.models.Node`
        """

        if node.pk and self.filter(pk=node.pk).exists():
            raise ValueError(
                _("Cannot insert a node which has already been saved."))

        if position not in Position:
            raise NotImplementedError("given position is not supported")

        if target is None:
            from mptt2.models import Tree
            node.mptt_tree = Tree.objects.create()
            node.mptt_lft = 1
            node.mptt_rgt = 2
            node.mptt_depth = 0
            node.parent = None
        else:
            self._calculate_node_mptt_values_for_insert(
                node=node, target=target, position=position)
            self.select_for_update().filter(
                self._calculate_filter_for_insert(
                    target=target, position=position)
            ).update(**self._calculate_conditional_update_for_insert(target=target, position=position))

        node.save()
        return node

    @atomic
    def move_node(self,
                  node,
                  target,
                  position=Position.LAST_CHILD):
        """Tree function to move a node relative to a given target by the given position

        :param target: The target node where the given node shall be inserted relative to.
        :type target: :class:`mptt2.models.Node`

        :param position: The relative position to the target
                         (Default: ``Position.LAST_CHILD``)
        :type position: :class:`mptt2.enums.Position`, optional

        :returns: the inserted node it self
        :rtype: :class:`mptt2.models.Node`
        """

        if node.mptt_tree != target.mptt_tree:
            raise InvalidMove(
                "moving nodes between trees is not supported")

        if position in [Position.LAST_CHILD, Position.FIRST_CHILD]:
            if node == target:
                raise InvalidMove(
                    _("A node may not be made a child of itself."))
            elif node.mptt_lft < target.mptt_lft < node.mptt_rgt:
                raise InvalidMove(
                    _("A node may not be made a child of any of its descendants.")
                )
            if position == Position.LAST_CHILD:
                if target.mptt_rgt > node.mptt_rgt:
                    new_left = target.mptt_rgt - node.subtree_width
                    new_right = target.mptt_rgt - 1
                else:
                    new_left = target.mptt_rgt
                    new_right = target.mptt_rgt + node.subtree_width - 1
            else:
                if target.mptt_lft > node.mptt_lft:
                    new_left = target.mptt_lft - node.subtree_width + 1
                    new_right = target.mptt_lft
                else:
                    new_left = target.mptt_lft + 1
                    new_right = target.mptt_lft + node.subtree_width
            depth_change = node.mptt_depth - target.mptt_depth - 1
            parent = target

        elif position in [Position.LEFT, Position.RIGHT]:
            if node == target:
                raise InvalidMove(
                    _("A node may not be made a sibling of itself."))
            elif node.mptt_lft < target.mptt_lft < node.mptt_rgt:
                raise InvalidMove(
                    _("A node may not be made a sibling of any of its descendants.")
                )
            if position == Position.LEFT:
                if target.mptt_lft > node.mptt_lft:
                    new_left = target.mptt_lft - node.subtree_width
                    new_right = target.mptt_lft - 1
                else:
                    new_left = target.mptt_lft
                    new_right = target.mptt_lft + node.subtree_width - 1
            else:
                if target.mptt_rgt > node.mptt_rgt:
                    new_left = target.mptt_rgt - node.subtree_width + 1
                    new_right = target.mptt_rgt
                else:
                    new_left = target.mptt_rgt + 1
                    new_right = target.mptt_rgt + node.subtree_width
            depth_change = node.mptt_depth - target.mptt_depth
            parent = target.mptt_parent
        else:
            raise ValueError(
                _("An invalid position was given: %s.") % position)

        left_boundary = min(node.mptt_lft, new_left)
        right_boundary = max(node.mptt_rgt, new_right)
        left_right_change = new_left - node.mptt_lft
        gap_size = node.subtree_width
        if left_right_change > 0:
            gap_size = -gap_size

        self.select_for_update().filter(
            mptt_tree=target.mptt_tree
        ).update(
            mptt_depth=Case(
                When(
                    condition=Q(mptt_lft__gte=node.mptt_lft,
                                mptt_lft__lte=node.mptt_rgt),
                    then=Depth() - depth_change
                ),
                default=Depth(),
                output_field=PositiveIntegerField()
            ),
            mptt_lft=Case(
                When(
                    condition=Q(mptt_lft__gte=node.mptt_lft,
                                mptt_lft__lte=node.mptt_rgt),
                    then=Left() + left_right_change
                ),
                When(
                    condition=Q(mptt_lft__gte=left_boundary,
                                mptt_lft__lte=right_boundary),
                    then=Left() + gap_size
                ),
                default=Left(),
                output_field=PositiveIntegerField()
            ),
            mptt_rgt=Case(
                When(
                    condition=Q(mptt_rgt__gte=node.mptt_lft,
                                mptt_rgt__lte=node.mptt_rgt),
                    then=Right() + left_right_change
                ),
                When(
                    condition=Q(mptt_rgt__gte=left_boundary,
                                mptt_rgt__lte=right_boundary),
                    then=Right() + gap_size
                ),
                default=Right(),
                output_field=PositiveIntegerField()
            )
        )

        node.mptt_lft = new_left
        node.mptt_rgt = new_right
        node.mptt_depth -= depth_change
        node.mptt_parent = parent
        node.save()
