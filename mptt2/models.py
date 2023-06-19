from django.db.models import Model
from django.db.models.constraints import CheckConstraint, UniqueConstraint
from django.db.models.deletion import CASCADE
from django.db.models.expressions import F
from django.db.models.fields import PositiveIntegerField
from django.db.models.fields.related import ForeignKey
from django.db.models.indexes import Index
from django.db.models.query import Q, QuerySet
from django.db.transaction import atomic
from django.utils.translation import gettext as _

from mptt2.compatibility import violation_error_message_kwargs
from mptt2.enums import Position
from mptt2.managers import TreeManager
from mptt2.query import (AncestorsQuery, ChildrenQuery, DescendantsQuery,
                         FamilyQuery, RootQuery, SiblingsQuery)


class Tree(Model):
    """Simple Tree model to generate simple tree id's by the database to support thread safe inserting new tree's"""
    pass


class Node(Model):
    """Abstract MPTT Node model, which implements all needed fields for nested sets.

    :param mptt_parent: A foreignkey to the parent node. None means it is the root node of a tree.
    :type mptt_parent: `ForeignKey <https://docs.djangoproject.com/en/4.2/ref/models/fields/#django.db.models.ForeignKey>`_, optional

    :param mptt_tree: A foreignkey to a unique tree object to differ between different trees.
    :type mptt_tree: ForeignKey

    :param mptt_lft: The left value of the node
    :type mptt_lft: int

    :param mptt_rgt: The right value of the node
    :type mptt_rgt: int

    :param mptt_depth: The hierarchy level of this node inside the tree
    :type mptt_depth: int

    """
    mptt_parent = ForeignKey(
        to="self",
        on_delete=CASCADE,
        null=True,
        related_name="chilren",
        related_query_name="child",
        editable=False,
        verbose_name=_("parent"),
        help_text=_("The parent of this node"),
    )
    mptt_tree = ForeignKey(
        to=Tree,
        on_delete=CASCADE,
        verbose_name=_("tree"),
        help_text=_("The unique tree, where this node is part of"),
        related_name="nodes",
        related_query_name="node",
        editable=False
    )
    mptt_lft = PositiveIntegerField(
        editable=False,
        verbose_name=_("left"),
        help_text=_("The left value of the node")
    )
    mptt_rgt = PositiveIntegerField(
        editable=False,
        verbose_name=_("right"),
        help_text=_("The right value of the node")
    )
    mptt_depth = PositiveIntegerField(
        editable=False,
        verbose_name=_("depth"),
        help_text=_("The hierarchy level of this node inside the tree")
    )

    objects: TreeManager = TreeManager()

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
                **violation_error_message_kwargs()
            ),
            # TODO: add unique constraint for lft and rgt fields
            # UniqueConstraint(fields=["mptt_tree_id", "mptt_lft"], name="unique_lft")
        ]

    def __str__(self) -> str:
        """returns pk | tree | lft | rgt"""
        return f"pk {self.pk} | tree {self.mptt_tree_id} | lft {self.mptt_lft} | rgt {self.mptt_rgt}"

    @atomic
    def delete(self, *args, **kwargs):
        """Custom delete function to update nested set values if a node and there descendants are deleted."""
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

    def get_children(self, asc=False) -> QuerySet:
        """returns a queryset representing the children of the current node

        :param asc: switch to sort the queryset ascending
        :type asc: bool

        """
        children = self.__class__.objects.filter(ChildrenQuery(of=self))
        return children.order_by("-mptt_lft") if asc else children

    def get_descendants(self, include_self=False, asc=False) -> QuerySet:
        """returns a queryset representing the descendants of the current node

        :param asc: switch to include the current node with the queryset
        :type asc: bool

        :param asc: switch to sort the queryset ascending
        :type asc: bool

        """
        descendants = self.__class__.objects.filter(
            DescendantsQuery(of=self, include_self=include_self))
        return descendants.order_by("-mptt_lft") if asc else descendants

    def get_ancestors(self, include_self=False, asc=False) -> QuerySet:
        """returns a queryset representing the ancestors of the current node

        :param asc: switch to include the current node with the queryset
        :type asc: bool

        :param asc: switch to sort the queryset ascending
        :type asc: bool

        """
        ancestors = self.__class__.objects.filter(
            AncestorsQuery(of=self, include_self=include_self))
        return ancestors.order_by("-mptt_lft") if asc else ancestors

    def get_family(self, include_self=False, asc=False) -> QuerySet:
        """returns a queryset representing the family of the current node (descendants and ancestors)

        :param asc: switch to include the current node with the queryset
        :type asc: bool

        :param asc: switch to sort the queryset ascending
        :type asc: bool

        """
        family = self.__class__.objects.filter(FamilyQuery(
            of=self, include_self=include_self))
        return family.order_by("-mptt_lft") if asc else family

    def get_siblings(self, include_self=False, asc=False) -> QuerySet:
        """returns a queryset representing siblings of the current node

        :param asc: switch to include the current node with the queryset
        :type asc: bool

        :param asc: switch to sort the queryset ascending
        :type asc: bool

        """
        siblings = self.__class__.objects.filter(
            SiblingsQuery(of=self, include_self=include_self))
        return siblings.order_by("-mptt_lft") if asc else siblings

    def get_root(self):
        """returns the root node of the tree where this node is part of"""
        return self.__class__.objects.get(RootQuery(of=self))

    def move_to(self, target, position: Position = Position.LAST_CHILD):
        """Tree function to move a node relative to a given target by the given position

        :param target: The target node where the given node shall be inserted relative to.
        :type target: :class:`mptt2.models.Node`

        :param position: The relative position to the target
                         (Default: ``Position.LAST_CHILD``)
        :type position: :class:`mptt2.enums.Position`, optional

        :returns: the inserted node it self
        :rtype: :class:`mptt2.models.Node`
        """
        return self.__class__.objects.move_node(
            node=self,
            target=target,
            position=position
        )

    def insert_at(self, target, position: Position = Position.LAST_CHILD):
        """Tree function to insert this node to a given target relative by the given position

        :param target: The target node where the given node shall be inserted relative to.
        :type target: :class:`mptt2.models.Node`

        :param position: The relative position to the target
                         (Default: ``Position.LAST_CHILD``)
        :type target: :class:`mptt2.enums.Position`, optional

        :returns: the inserted node it self
        :rtype: :class:`mptt2.models.Node`
        """
        return self.__class__.objects.insert_node(
            node=self,
            target=target,
            position=position
        )

    @ property
    def is_root_node(self) -> bool:
        """returns True if this is the root of the tree"""
        return self.mptt_parent is None

    @ property
    def is_leaf_node(self) -> bool:
        """returns true if this is a leaf node without children"""
        return (self.mptt_rgt - self.mptt_lft) // 2 == 0

    @ property
    def has_leafs(self) -> bool:
        """returns true if this node has leafs (descendants)"""
        return self.mptt_rgt - self.mptt_lft > 1

    @ property
    def descendant_count(self) -> int:
        """returns the descendant count"""
        if self.mptt_rgt is None:
            # node not saved yet
            return 0
        else:
            return (self.mptt_rgt - self.mptt_lft - 1) // 2

    @ property
    def subtree_width(self) -> int:
        """returns the width of the left and right attribute which are used from descendants"""
        return self.mptt_rgt - self.mptt_lft + 1
