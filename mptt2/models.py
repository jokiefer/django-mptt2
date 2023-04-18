from django.db.models import Model
from django.db.models.fields import PositiveIntegerField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE
from django.db.models.query import QuerySet
from django.db.models.indexes import Index
from django.db.models.constraints import CheckConstraint, UniqueConstraint
from django.db.models.query import Q
from django.db.models.expressions import F
from django.utils.translation import gettext as _


from mptt2.query import DescendantsQuery, AncestorsQuery, FamilyQuery, SiblingsQuery, TreeQuerySet


class Tree(Model):
    pass


class Node(Model):
    mptt_parent = ForeignKey(to="self", on_delete=CASCADE)
    mptt_tree = ForeignKey(to=Tree, on_delete=CASCADE)
    mptt_lft = PositiveIntegerField()
    mptt_rgt = PositiveIntegerField()
    mptt_depth = PositiveIntegerField()

    objects = TreeQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ["mptt_tree_id", "mptt_lft"]
        indexes = [
            Index(fields=("mptt_tree_id", "mptt_lft", "mptt_rgt"))
        ]
        constraints = [
            CheckConstraint(
                check=Q(mptt_rgt_gt=F("mptt_lft")), 
                name="rgt_gt_lft",
                violation_error_message=_("The right side value rgt is allways greater than the node left side value lft.")
            ),
            CheckConstraint(
                check=Q()
            ),
            UniqueConstraint(
                fields=["mptt_tree_id", "mptt_lft"],
                name="unique_tree_node_lft_check",
                violation_error_message=_("A node with the same lft value exists for this tree.")
            ),
            UniqueConstraint(
                fields=["mptt_tree_id", "mptt_rgt"],
                name="unique_tree_node_rgt_check",
                violation_error_message=_("A node with the same rgt value exists for this tree.")
            )
        ]

    
    def get_descendants(self, include_self=False, asc=False)-> QuerySet:
        descendants = self.objects.filter(DescendantsQuery(include_self=include_self))
        return descendants.order_by("-mptt_lft") if asc else descendants

    def get_ancestors(self, include_self=False, asc=False) -> QuerySet:
        ancestors = self.objects.filter(AncestorsQuery(include_self=include_self))
        return ancestors.order_by("-mptt_lft") if asc else ancestors

    def get_family(self, include_self=False, asc=False) -> QuerySet:
        family = self.objects.filter(FamilyQuery(include_self=include_self))
        return family.order_by("-mptt_lft") if asc else family
    
    def get_siblings(self, include_self=False, asc=False) -> QuerySet:
        siblings = self.objects.filter(SiblingsQuery(include_self=include_self))
        return siblings.order_by("-mptt_lft") if asc else siblings
    
    def is_root_node(self) -> bool:
        return self.parent is None
    
    def is_leaf_node(self):
        return (self.mptt_rgt - self.mptt_lft) // 2 == 0
    
    def get_descendant_count(self):
        if self.mptt_rgt is None:
            # node not saved yet
            return 0
        else:
            return (self.mptt_rgt - self.mptt_lft - 1) // 2