from django.db.models import Model
from django.db.models.fields import PositiveIntegerField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE
from django.db.models.query import QuerySet
from django.db.models.indexes import Index
from mptt2.query import DescendantsQuery, AncestorsQuery, FamilyQuery, SiblingsQuery, TreeQuerySet


class Tree(Model):
    pass


class Node(Model):
    parent = ForeignKey(to="self", on_delete=CASCADE)
    mptt_tree_id = ForeignKey(to=Tree, on_delete=CASCADE)
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
    
    