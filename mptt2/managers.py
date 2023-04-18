from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.db.models.expressions import F
from django.db.transaction import atomic

from mptt2.query import TreeQuerySet
from mptt2.models import Node, Tree



class TreeManager(Manager):
    
    def get_queryset(self) -> QuerySet[TreeQuerySet]:
        return TreeQuerySet(self.model, using=self._db)

    def insert_node(self,
        node: Node,
        target: Node,
        position: str = "last-child",
        allow_existing_pk: bool = False,
        refresh_target: bool = True,):

        if node.pk and not allow_existing_pk and self.filter(pk=node.pk).exists():
            raise ValueError(_("Cannot insert a node which has already been saved."))

        if target is None:
            node.mptt_lft = 1
            node.mptt_rgt = 2
            node.mptt_depth = 0
            node.mptt_tree = Tree()
            node.parent = None
        elif position == "last-child":
            node.mptt_parent = target
            node.mptt_lft = target.rgt
            node.mptt_rgt = target.rgt + 1
            node.mptt_depth = target.mptt_depth + 1

            with atomic():
                self.filter(mptt_rgt_gte=target.rgt).update(mptt_rgt=F("mptt_rgt") + 2)
                self.filter(mptt_lft_lt=target.rgt).update(mptt_lft=F("mptt_lft") + 2 )
                node.save()
        return node