

from django.db.models.fields import CharField

from mptt2.models import Node


class SimpleNode(Node):
    title = CharField(max_length=10, default="some node")



class OtherNode(Node):
    title = CharField(max_length=10, default="some node")