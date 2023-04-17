from django.db.models import Model
from django.db.models.fields import PositiveIntegerField
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE


class Tree(Model):
    pass


class Node(Model):
    mptt_tree_id = ForeignKey(to=Tree, on_delete=CASCADE)
    mptt_lft = PositiveIntegerField()
    mptt_rgt = PositiveIntegerField()
    mptt_depth = PositiveIntegerField()
