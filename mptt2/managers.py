from django.db.models.expressions import F
from django.db.models.manager import Manager
from django.db.models.query import Q, QuerySet
from django.db.transaction import atomic
from django.utils.translation import gettext as _

from mptt2.enums import Position
from mptt2.query import (DescendantsQuery, RootQuery, SameTreeQuery,
                         TreeQuerySet)


class TreeManager(Manager):

    def get_queryset(self) -> QuerySet[TreeQuerySet]:
        return TreeQuerySet(self.model, using=self._db)

    # FIXME: code of all position checking branches could be merged with some additional logic
    # FIXME: create query object to get right sibling and there descendants
    @atomic
    def insert_node(self,
                    node,
                    target=None,
                    position: Position = Position.LAST_CHILD.value):

        if node.pk and self.filter(pk=node.pk).exists():
            raise ValueError(
                _("Cannot insert a node which has already been saved."))

        if target is None:
            from mptt2.models import Tree
            node.mptt_tree = Tree.objects.create()
            node.mptt_lft = 1
            node.mptt_rgt = 2
            node.mptt_depth = 0
            node.parent = None
        elif position == Position.LAST_CHILD.value:
            node.mptt_parent = target
            node.mptt_tree = target.mptt_tree
            node.mptt_depth = target.mptt_depth + 1
            node.mptt_lft = target.mptt_rgt
            node.mptt_rgt = target.mptt_rgt + 1
            with atomic():
                self.filter(SameTreeQuery(mptt_rgt__gte=target.mptt_rgt)).update(
                    mptt_rgt=F("mptt_rgt") + 2)
                self.filter(SameTreeQuery(mptt_lft__gt=target.mptt_rgt)).update(
                    mptt_lft=F("mptt_lft") + 2)
        elif position == Position.FIRST_CHILD.value:
            node.mptt_parent = target
            node.mptt_tree = target.mptt_tree
            node.mptt_depth = target.mptt_depth + 1
            node.mptt_lft = target.mptt_lft + 1
            node.mptt_rgt = target.mptt_lft + 2

            with atomic():
                self.filter(SameTreeQuery(mptt_rgt__gte=target.mptt_lft)).update(
                    mptt_rgt=F("mptt_rgt") + 2)
                self.filter(SameTreeQuery(mptt_lft__gt=target.mptt_lft)).update(
                    mptt_lft=F("mptt_lft") + 2)
        elif position == Position.LEFT.value:
            node.mptt_parent = target
            node.mptt_tree = target.mptt_tree
            node.mptt_depth = target.mptt_depth
            node.mptt_lft = target.mptt_lft
            node.mptt_rgt = target.mptt_lft + 1
            with atomic():
                self.filter(SameTreeQuery(mptt_lft__gte=target.mptt_lft)).update(
                    mptt_lft=F("mptt_lft") + 2, mptt_rgt=F("mptt_rgt") + 2)
                self.filter(RootQuery()).update(
                    mptt_rgt=F("mptt_rgt") + 2)
        elif position == Position.RIGHT.value:
            node.mptt_parent = target
            node.mptt_tree = target.mptt_tree
            node.mptt_depth = target.mptt_depth
            node.mptt_lft = target.mptt_rgt + 1
            node.mptt_rgt = target.mptt_rgt + 2
            with atomic():
                self.filter(SameTreeQuery(mptt_rgt__gt=target.mptt_rgt)).update(
                    mptt_rgt=F("mptt_rgt") + 2)
                self.filter(SameTreeQuery(mptt_lft__gt=target.mptt_rgt)).update(
                    mptt_lft=F("mptt_lft") + 2)
        else:
            raise NotImplementedError("given position is not supported")
        node.save()
        return node

    @atomic
    def move_node(self,
                  node,
                  target,
                  position=Position.LAST_CHILD.value,
                  ):
        if position == Position.LEFT.value:

            # update target subtree
            target_subtree = self.select_for_update().filter(
                DescendantsQuery(of=target, include_self=True)
            )
            for _node in target_subtree:
                _node.mptt_lft += node.subtree_width
                _node.mptt_rgt += node.subtree_width

            # update node subtree
            node_subtree = self.select_for_update().filter(
                DescendantsQuery(of=node, include_self=True)
            )
            for _node in node_subtree:
                _node.mptt_lft -= target.subtree_width
                _node.mptt_rgt -= target.subtree_width

            objs = list(target_subtree) + list(node_subtree)

            self.bulk_update(objs=objs, fields=[
                "mptt_lft", "mptt_rgt"])

        else:
            raise NotImplementedError("given position is not supported")
