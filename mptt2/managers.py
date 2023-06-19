from typing import Dict, Tuple

from django.db.models import Case, Q, When
from django.db.models.fields import PositiveIntegerField
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.db.transaction import atomic
from django.utils.translation import gettext as _

from mptt2.enums import Position
from mptt2.exceptions import InvalidInsert, InvalidMove
from mptt2.expressions import Depth, Left, Right
from mptt2.query import (AncestorsQuery, DescendantsQuery,
                         RightSiblingsWithDescendants, RootQuery,
                         SameNodeQuery, TreeQuerySet)


class TreeManager(Manager):

    queryset_class = TreeQuerySet

    def get_queryset(self) -> QuerySet[queryset_class]:
        return self.queryset_class(self.model, using=self._db)

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
                    of=target, include_self=True if position == Position.LAST_CHILD else False)  |
                AncestorsQuery(of=target)
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
            condition &= ~SameNodeQuery(of=target) & ~ AncestorsQuery(of=target)

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

    def _validate_insert(self, node, target, position):
        if node.pk and self.filter(pk=node.pk).exists():
            raise ValueError(
                _("Cannot insert a node which has already been saved."))

        if position not in Position:
            raise NotImplementedError(_("given position is not supported"))

        if position in [Position.LEFT, Position.RIGHT] and target.is_root_node:
            raise InvalidInsert(_("You can't insert a second root node."))

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

        self._validate_insert(node, target, position)

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

    def _validate_move(self, node, target, position):
        if node.mptt_tree != target.mptt_tree:
            raise InvalidMove(
                _("moving nodes between trees is not supported"))

        if position not in [Position.LAST_CHILD, Position.FIRST_CHILD, Position.LEFT, Position.RIGHT]:

            raise ValueError(
                _("An invalid position was given: %s.") % position)

        base_msg = _("A node may not be made a {move_kind} of {relatedness}")
        move_kind_i18n = _(
            "child") if position in [Position.LAST_CHILD, Position.FIRST_CHILD] else _("sibling")
        if node == target:
            relatedness = _("itself")
            msg = base_msg.format(move_kind=move_kind_i18n,
                                  relatedness=relatedness)
            raise InvalidMove(msg)
        elif node.mptt_lft < target.mptt_lft < node.mptt_rgt:
            relatedness = _("its descendants.")
            msg = base_msg.format(move_kind=move_kind_i18n,
                                  relatedness=relatedness)
            raise InvalidMove(msg)

    def _calculate_move_changes(self, node, target, position) -> Tuple:
        if position in [Position.LAST_CHILD, Position.FIRST_CHILD]:
            depth_change = node.mptt_depth - target.mptt_depth - 1
            parent = target
        elif position in [Position.LEFT, Position.RIGHT]:
            depth_change = node.mptt_depth - target.mptt_depth
            parent = target.mptt_parent

        if position == Position.LAST_CHILD:
            if target.mptt_rgt > node.mptt_rgt:
                new_left = target.mptt_rgt - node.subtree_width
                new_right = target.mptt_rgt - 1
            else:
                new_left = target.mptt_rgt
                new_right = target.mptt_rgt + node.subtree_width - 1
        elif position == Position.LEFT:
            if target.mptt_lft > node.mptt_lft:
                new_left = target.mptt_lft - node.subtree_width
                new_right = target.mptt_lft - 1
            else:
                new_left = target.mptt_lft
                new_right = target.mptt_lft + node.subtree_width - 1

        elif position == Position.FIRST_CHILD:
            if target.mptt_lft > node.mptt_lft:
                new_left = target.mptt_lft - node.subtree_width + 1
                new_right = target.mptt_lft
            else:
                new_left = target.mptt_lft + 1
                new_right = target.mptt_lft + node.subtree_width
        elif position == Position.RIGHT:
            if target.mptt_rgt > node.mptt_rgt:
                new_left = target.mptt_rgt - node.subtree_width + 1
                new_right = target.mptt_rgt
            else:
                new_left = target.mptt_rgt + 1
                new_right = target.mptt_rgt + node.subtree_width

        left_boundary = min(node.mptt_lft, new_left)
        right_boundary = max(node.mptt_rgt, new_right)
        left_right_change = new_left - node.mptt_lft
        gap_size = node.subtree_width
        if left_right_change > 0:
            gap_size = -gap_size

        return new_left, new_right, depth_change, parent, left_boundary, right_boundary, left_right_change, gap_size

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

        self._validate_move(node, target, position)

        new_left, new_right, depth_change, parent, left_boundary, right_boundary, left_right_change, gap_size = self._calculate_move_changes(
            node, target, position)

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
