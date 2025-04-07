

from django.db.models.fields import CharField
from django.db.models import Manager
from mptt2.models import Node
from mptt2.managers import TreeManager


class SomeOtherManager(Manager):
    pass

class SomeManager(SomeOtherManager, TreeManager):
    pass


class SimpleNode(Node):
    title = CharField(max_length=10, default="some node")
    objects = SomeManager()


class OtherNode(Node):
    title = CharField(max_length=10, default="some node")
