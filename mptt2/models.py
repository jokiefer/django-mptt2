from django.db.models import Model
from django.db.models.fields import PositiveIntegerField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE
from django.db.models.query import QuerySet

from mptt2.query import DescendantsQuery, AncestorsQuery, FamilyQuery, TreeQuerySet


class Tree(Model):
    pass


class Node(Model):
    mptt_tree_id = ForeignKey(to=Tree, on_delete=CASCADE)
    mptt_lft = PositiveIntegerField()
    mptt_rgt = PositiveIntegerField()
    mptt_depth = PositiveIntegerField()

    objects = TreeQuerySet.as_manager()

    class Meta:
        ordering = ["mptt_tree_id", "mptt_lft"]

        # TODO: indexes

    def get_descendants(self, include_self=False)-> QuerySet:
        self.objects.filter(DescendantsQuery(include_self=include_self))

    def get_ancestors(self, include_self=False) -> QuerySet:
        self.objects.filter(AncestorsQuery(include_self=include_self))

    def get_family(self, include_self=False) -> QuerySet:
        self.objects.filter(FamilyQuery(include_self=include_self))