from django.db.models.expressions import F
from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.db.transaction import atomic
from django.utils.translation import gettext as _

from mptt2.enums import Position
from mptt2.query import TreeQuerySet


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
                self.filter(mptt_tree=F("mptt_tree"), mptt_rgt__gte=target.mptt_rgt).update(
                    mptt_rgt=F("mptt_rgt") + 2)
                self.filter(mptt_tree=F("mptt_tree"), mptt_lft__gt=target.mptt_rgt).update(
                    mptt_lft=F("mptt_lft") + 2)
        elif position == Position.FIRST_CHILD.value:
            node.mptt_parent = target
            node.mptt_tree = target.mptt_tree
            node.mptt_depth = target.mptt_depth + 1
            node.mptt_lft = target.mptt_lft + 1
            node.mptt_rgt = target.mptt_lft + 2

            with atomic():
                self.filter(mptt_tree=F("mptt_tree"), mptt_rgt__gte=target.mptt_lft).update(
                    mptt_rgt=F("mptt_rgt") + 2)
                self.filter(mptt_tree=F("mptt_tree"), mptt_lft__gt=target.mptt_lft).update(
                    mptt_lft=F("mptt_lft") + 2)
        elif position == Position.LEFT.value:
            node.mptt_parent = target
            node.mptt_tree = target.mptt_tree
            node.mptt_depth = target.mptt_depth
            node.mptt_lft = target.mptt_lft
            node.mptt_rgt = target.mptt_lft + 1
            with atomic():
                self.filter(mptt_tree=F("mptt_tree"), mptt_lft__gte=target.mptt_lft).update(
                    mptt_lft=F("mptt_lft") + 2, mptt_rgt=F("mptt_rgt") + 2)
                self.filter(mptt_tree=F("mptt_tree"), mptt_parent=None).update(
                    mptt_rgt=F("mptt_rgt") + 2)
        elif position == Position.RIGHT.value:
            node.mptt_parent = target
            node.mptt_tree = target.mptt_tree
            node.mptt_depth = target.mptt_depth
            node.mptt_lft = target.mptt_rgt + 1
            node.mptt_rgt = target.mptt_rgt + 2
            with atomic():
                self.filter(mptt_tree=F("mptt_tree"), mptt_rgt__gt=target.mptt_rgt).update(
                    mptt_rgt=F("mptt_rgt") + 2)
                self.filter(mptt_tree=F("mptt_tree"), mptt_lft__gt=target.mptt_rgt).update(
                    mptt_lft=F("mptt_lft") + 2)
        else:
            raise NotImplementedError("given position is not supported")
        node.save()
        return node
