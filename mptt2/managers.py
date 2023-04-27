from typing import Dict

from django.db.models import Case, Q, Value, When
from django.db.models.fields import PositiveIntegerField
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.db.transaction import atomic
from django.utils.translation import gettext as _

from mptt2.enums import Position
from mptt2.exceptions import InvalidMove
from mptt2.expressions import Left, Right
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

        elif position == Position.LEFT:
            if target.mptt_lft - node.mptt_rgt == 1:
                # do nothing. Given node is the left sibling of the given target.
                return

            _update = {
                "mptt_lft": Case(
                    When(
                        condition=IsDescendantOfQuery(
                            of=node, include_self=True),
                        then=Left() - Value(target.subtree_width)
                    ),
                    default=Left() + Value(node.subtree_width),
                    output_field=PositiveIntegerField()
                ),
                "mptt_rgt": Case(
                    When(
                        condition=IsDescendantOfQuery(
                            of=node, include_self=True),
                        then=Right() - Value(target.subtree_width)
                    ),
                    default=Right() + Value(node.subtree_width),
                    output_field=PositiveIntegerField()
                ),
            }

            self.select_for_update().filter(
                DescendantsQuery(of=node, include_self=True) |
                DescendantsQuery(of=target, include_self=True)
            ).update(
                **_update
            )

        elif position == Position.RIGHT:
            if node.mptt_lft - target.mptt_rgt == 1:
                # do nothing. Given node is the right sibling of the given target.
                return
            right_subtrees_width = target.mptt_rgt - node.mptt_lft + 1

            # update target subtree
            siblings_with_descendants = self.select_for_update().filter(
                mptt_tree=node.mptt_tree,
                mptt_lft__gt=node.mptt_lft,
                mptt_rgt__lte=target.mptt_rgt
            )
            for _node in siblings_with_descendants:
                _node.mptt_lft -= node.subtree_width
                _node.mptt_rgt -= node.subtree_width

            # update node subtree
            node_subtree = self.select_for_update().filter(
                DescendantsQuery(of=node, include_self=True)
            )
            for _node in node_subtree:
                _node.mptt_lft += right_subtrees_width - node.subtree_width
                _node.mptt_rgt += right_subtrees_width - node.subtree_width

            objs = list(node_subtree) + list(siblings_with_descendants)

            self.bulk_update(objs=objs, fields=["mptt_lft", "mptt_rgt"])

        elif position == Position.FIRST_CHILD:
            if node.mptt_lft - target.mptt_lft == 1:
                # do nothing. Given node is already the first child of the target.
                return
            jump_width = node.mptt_lft - target.mptt_lft - 1

            node_subtree = self.select_for_update().filter(
                DescendantsQuery(of=node, include_self=True)
            )

            level_increment_base = None
            for _node in node_subtree:
                if level_increment_base == None:
                    level_increment_base = 0 if node.mptt_depth - \
                        target.mptt_depth == 1 else node.mptt_depth - target.mptt_depth - 1
                    _node.mptt_parent = target

                _node.mptt_depth += abs(
                    level_increment_base) if level_increment_base < 0 else - level_increment_base

                _node.mptt_lft -= jump_width
                _node.mptt_rgt -= jump_width

            target_subtree = self.select_for_update().filter(
                DescendantsQuery(of=target, include_self=True)
            )

            for _node in target_subtree:
                # skip incrementing lft of target
                _node.mptt_lft += node.subtree_width if _node.mptt_lft != target.mptt_lft else 0
                _node.mptt_rgt += node.subtree_width

            node_left_side_siblings_with_descendants = self.select_for_update().filter(
                mptt_tree=node.mptt_tree,
                mptt_lft__gt=target.mptt_rgt,
                mptt_rgt__lt=node.mptt_lft
            )

            for _node in node_left_side_siblings_with_descendants:
                _node.mptt_lft += node.subtree_width + 1
                _node.mptt_rgt += node.subtree_width + 1

            objs = list(node_subtree) + \
                list(node_left_side_siblings_with_descendants) + \
                list(target_subtree)

            self.bulk_update(
                objs=objs,
                fields=["mptt_depth", "mptt_lft", "mptt_rgt", "mptt_parent"]
            )

        elif position == Position.LAST_CHILD:
            if node.mptt_rgt - target.mptt_rgt == 1:
                # do nothing. Given node is already the last child of the target
                return
            jump_width = node.mptt_lft - target.mptt_rgt

            node_subtree = self.select_for_update().filter(
                DescendantsQuery(of=node, include_self=True)
            )
            level_increment_base = None
            for _node in node_subtree:
                if level_increment_base == None:
                    level_increment_base = 0 if node.mptt_depth - \
                        target.mptt_depth == 1 else node.mptt_depth - target.mptt_depth - 1
                    _node.mptt_parent = target

                _node.mptt_depth += abs(
                    level_increment_base) if level_increment_base < 0 else - level_increment_base
                _node.mptt_lft -= jump_width
                _node.mptt_rgt -= jump_width

            target_with_right_side_siblings_with_descendants = self.select_for_update().filter(
                mptt_tree=node.mptt_tree,
                mptt_lft__lt=node.mptt_lft,
                mptt_rgt__gte=target.mptt_rgt
            )

            for _node in target_with_right_side_siblings_with_descendants:
                _node.mptt_lft += node.subtree_width if _node.mptt_lft >= target.mptt_rgt else 0
                _node.mptt_rgt += node.subtree_width if _node.mptt_rgt <= node.mptt_rgt else 0

            objs = list(node_subtree) + \
                list(target_with_right_side_siblings_with_descendants)

            self.bulk_update(
                objs=objs,
                fields=["mptt_depth", "mptt_lft", "mptt_rgt", "mptt_parent"]
            )
            return node.refresh_from_db()

        else:
            raise NotImplementedError("given position is not supported")
