from django.db.models import Model
from django.db.models.constraints import CheckConstraint
from django.db.models.deletion import CASCADE
from django.db.models.expressions import F
from django.db.models.fields import PositiveIntegerField
from django.db.models.fields.related import ForeignKey
from django.db.models.indexes import Index
from django.db.models.query import Q, QuerySet
from django.db.transaction import atomic
from django.utils.translation import gettext as _

from mptt2.managers import TreeManager
from mptt2.query import (AncestorsQuery, DescendantsQuery, FamilyQuery,
                         SiblingsQuery)


class Tree(Model):
    pass


class Node(Model):
    mptt_parent = ForeignKey(to="self", on_delete=CASCADE, null=True)
    mptt_tree = ForeignKey(to=Tree, on_delete=CASCADE)
    mptt_lft = PositiveIntegerField()
    mptt_rgt = PositiveIntegerField()
    mptt_depth = PositiveIntegerField()

    objects = TreeManager()

    class Meta:
        abstract = True
        ordering = ["mptt_tree_id", "mptt_lft"]
        indexes = [
            Index(fields=("mptt_tree_id", "mptt_lft", "mptt_rgt"))
        ]
        constraints = [
            CheckConstraint(
                check=Q(mptt_rgt__gt=F("mptt_lft")),
                name="rgt_gt_lft",
                violation_error_message=_(
                    "The right side value rgt is allways greater than the node left side value lft."),
            )
            # UniqueConstraint(
            #     fields=["mptt_tree_id", "mptt_lft"],
            #     # condition=Q(mptt_tree__mptt_tree_update__istrue=False), --> django.core.exceptions.FieldError: Joined field references are not permitted in this query
            #     name="unique_tree_node_lft_check",
            #     violation_error_message=_("A node with the same lft value exists for this tree.")
            # ),
            # UniqueConstraint(
            #     fields=["mptt_tree_id", "mptt_rgt"],
            #     # condition=Q(mptt_tree__mptt_tree_update__istrue=False), --> django.core.exceptions.FieldError: Joined field references are not permitted in this query
            #     name="unique_tree_node_rgt_check",
            #     violation_error_message=_("A node with the same rgt value exists for this tree.")
            # )
        ]

    def __str__(self) -> str:
        return f"{self.mptt_tree_id} | {self.mptt_lft} | {self.mptt_rgt}"

    @atomic
    def delete(self, *args, **kwargs):
        del_return = super().delete(*args, **kwargs)
        self.__class__.objects.filter(
            mptt_tree=self.mptt_tree,
            mptt_lft__gt=self.mptt_rgt
        ).update(
            mptt_lft=F("mptt_lft") - self.subtree_width
        )
        self.__class__.objects.filter(
            mptt_tree=self.mptt_tree,
            mptt_rgt__gt=self.mptt_rgt
        ).update(
            mptt_rgt=F("mptt_rgt") - self.subtree_width
        )

        return del_return

    def move_to(self):
        # TODO:
        pass

    def get_descendants(self, include_self=False, asc=False) -> QuerySet:
        # FIXME: not based on the current node
        descendants = self.objects.filter(
            DescendantsQuery(include_self=include_self))
        return descendants.order_by("-mptt_lft") if asc else descendants

    def get_ancestors(self, include_self=False, asc=False) -> QuerySet:
        # FIXME: not based on the current node
        ancestors = self.objects.filter(
            AncestorsQuery(include_self=include_self))
        return ancestors.order_by("-mptt_lft") if asc else ancestors

    def get_family(self, include_self=False, asc=False) -> QuerySet:
        # FIXME: not based on the current node
        family = self.objects.filter(FamilyQuery(include_self=include_self))
        return family.order_by("-mptt_lft") if asc else family

    def get_siblings(self, include_self=False, asc=False) -> QuerySet:
        # FIXME: not based on the current node
        siblings = self.objects.filter(
            SiblingsQuery(include_self=include_self))
        return siblings.order_by("-mptt_lft") if asc else siblings

    @ property
    def is_root_node(self) -> bool:
        return self.parent is None

    @ property
    def is_leaf_node(self) -> bool:
        return (self.mptt_rgt - self.mptt_lft) // 2 == 0

    @ property
    def has_leafs(self) -> bool:
        return self.mptt_rgt - self.mptt_lft > 0

    @ property
    def descendant_count(self):
        if self.mptt_rgt is None:
            # node not saved yet
            return 0
        else:
            return (self.mptt_rgt - self.mptt_lft - 1) // 2

    @ property
    def subtree_width(self):
        return self.mptt_rgt - self.mptt_lft + 1
