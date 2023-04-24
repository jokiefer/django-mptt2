from django.db.models.expressions import F, OuterRef
from django.db.models.query_utils import Q
from django.test import SimpleTestCase

from mptt2.query import (AncestorsQuery, ChildrenQuery, DescendantsQuery,
                         FamilyQuery, LeafNodesQuery, ParentQuery,
                         SiblingsQuery)


class QTestMixin(object):

    def assertQEqual(self, left, right):
        """
        Assert `Q` objects are equal by ensuring that their
        unicode outputs are equal (crappy but good enough)
        """
        self.assertIsInstance(left, Q)
        self.assertIsInstance(right, Q)
        self.assertEqual(str(left), str(right))


class TestParentQuery(QTestMixin, SimpleTestCase):

    def test_default_query(self):
        query = ParentQuery()
        expected = Q(
            mptt_lft=F("mptt_lft") - 1,
            mptt_rgt=F("mptt_rgt") + 1,
            mptt_tree=F("mptt_tree"))
        self.assertQEqual(expected, query)

    def test_parent_subquery(self):
        query = ParentQuery()
        query.to_subquery()
        expected = Q(
            mptt_lft=OuterRef("mptt_lft") - 1,
            mptt_rgt=OuterRef("mptt_rgt") + 1,
            mptt_tree=OuterRef("mptt_tree"))
        self.assertQEqual(expected, query)


class TestDescendantsQuery(QTestMixin, SimpleTestCase):

    def test_default_query(self):
        query = DescendantsQuery()
        expected = Q(
            mptt_lft_lt=F("mptt_lft"),
            mptt_rgt_gt=F("mptt_rgt"),
            mptt_tree=F("mptt_tree"))
        self.assertQEqual(expected, query)

    def test_default_query_include_self(self):
        query = DescendantsQuery(include_self=True)
        expected = Q(
            mptt_lft_lte=F("mptt_lft"),
            mptt_rgt_gte=F("mptt_rgt"),
            mptt_tree=F("mptt_tree"))
        self.assertQEqual(expected, query)

    def test_subquery(self):
        query = DescendantsQuery()
        query.to_subquery()
        expected = Q(
            mptt_lft_lt=OuterRef("mptt_lft"),
            mptt_rgt_gt=OuterRef("mptt_rgt"),
            mptt_tree=OuterRef("mptt_tree"))
        self.assertQEqual(expected, query)

    def test_subquery_include_self(self):
        query = DescendantsQuery(include_self=True)
        query.to_subquery()
        expected = Q(
            mptt_lft_lte=OuterRef("mptt_lft"),
            mptt_rgt_gte=OuterRef("mptt_rgt"),
            mptt_tree=OuterRef("mptt_tree"))
        self.assertQEqual(expected, query)


class TestAncestorsQuery(QTestMixin, SimpleTestCase):

    def test_default_query(self):
        query = AncestorsQuery()
        expected = Q(
            mptt_lft_gt=F("mptt_lft"),
            mptt_rgt_lt=F("mptt_rgt"),
            mptt_tree=F("mptt_tree"))
        self.assertQEqual(expected, query)

    def test_default_query_include_self(self):
        query = AncestorsQuery(include_self=True)
        expected = Q(
            mptt_lft_gte=F("mptt_lft"),
            mptt_rgt_lte=F("mptt_rgt"),
            mptt_tree=F("mptt_tree"))
        self.assertQEqual(expected, query)

    def test_subquery(self):
        query = AncestorsQuery()
        query.to_subquery()
        expected = Q(
            mptt_lft_gt=OuterRef("mptt_lft"),
            mptt_rgt_lt=OuterRef("mptt_rgt"),
            mptt_tree=OuterRef("mptt_tree"))
        self.assertQEqual(expected, query)

    def test_subquery_include_self(self):
        query = AncestorsQuery(include_self=True)
        query.to_subquery()
        expected = Q(
            mptt_lft_gte=OuterRef("mptt_lft"),
            mptt_rgt_lte=OuterRef("mptt_rgt"),
            mptt_tree=OuterRef("mptt_tree"))
        self.assertQEqual(expected, query)


class TestFamilyQuery(QTestMixin, SimpleTestCase):

    def test_default_query(self):
        query = FamilyQuery()
        expected = Q(
            mptt_lft_lt=F("mptt_lft"),
            mptt_rgt_gt=F("mptt_rgt"),
            mptt_tree=F("mptt_tree")) | Q(
            mptt_lft_gt=F("mptt_lft"),
            mptt_rgt_lt=F("mptt_rgt"),
            mptt_tree=F("mptt_tree"))
        self.assertQEqual(expected, query)

    def test_default_query_include_self(self):
        query = FamilyQuery(include_self=True)
        expected = Q(
            mptt_lft_lte=F("mptt_lft"),
            mptt_rgt_gte=F("mptt_rgt"),
            mptt_tree=F("mptt_tree")) | Q(
            mptt_lft_gte=F("mptt_lft"),
            mptt_rgt_lte=F("mptt_rgt"),
            mptt_tree=F("mptt_tree"))
        self.assertQEqual(expected, query)

    def test_subquery(self):
        query = FamilyQuery()
        query.to_subquery()
        expected = Q(
            mptt_lft_lt=OuterRef("mptt_lft"),
            mptt_rgt_gt=OuterRef("mptt_rgt"),
            mptt_tree=OuterRef("mptt_tree")) | Q(
            mptt_lft_gt=OuterRef("mptt_lft"),
            mptt_rgt_lt=OuterRef("mptt_rgt"),
            mptt_tree=OuterRef("mptt_tree"))
        self.assertQEqual(expected, query)

    def test_subquery_include_self(self):
        query = FamilyQuery(include_self=True)
        query.to_subquery()
        expected = Q(
            mptt_lft_lte=OuterRef("mptt_lft"),
            mptt_rgt_gte=OuterRef("mptt_rgt"),
            mptt_tree=OuterRef("mptt_tree")) | Q(
            mptt_lft_gte=OuterRef("mptt_lft"),
            mptt_rgt_lte=OuterRef("mptt_rgt"),
            mptt_tree=OuterRef("mptt_tree"))
        self.assertQEqual(expected, query)


class TestChildrenQuery(QTestMixin, SimpleTestCase):

    def test_default_query(self):
        query = ChildrenQuery()
        expected = Q(
            mptt_lft_lt=F("mptt_lft"),
            mptt_rgt_gt=F("mptt_rgt"),
            mptt_tree=F("mptt_tree"),
            mptt_depth=F("mptt_depth") + 1)
        self.assertQEqual(expected, query)

    def test_default_query_include_self(self):
        query = ChildrenQuery(include_self=True)
        expected = Q(
            mptt_lft_lte=F("mptt_lft"),
            mptt_rgt_gte=F("mptt_rgt"),
            mptt_tree=F("mptt_tree"),
            mptt_depth=F("mptt_depth") + 1)
        self.assertQEqual(expected, query)

    def test_subquery(self):
        query = ChildrenQuery()
        query.to_subquery()
        expected = Q(
            mptt_lft_lt=OuterRef("mptt_lft"),
            mptt_rgt_gt=OuterRef("mptt_rgt"),
            mptt_tree=OuterRef("mptt_tree"),
            mptt_depth=OuterRef("mptt_depth") + 1)
        self.assertQEqual(expected, query)

    def test_subquery_include_self(self):
        query = ChildrenQuery(include_self=True)
        query.to_subquery()
        expected = Q(
            mptt_lft_lte=OuterRef("mptt_lft"),
            mptt_rgt_gte=OuterRef("mptt_rgt"),
            mptt_tree=OuterRef("mptt_tree"),
            mptt_depth=OuterRef("mptt_depth") + 1)
        self.assertQEqual(expected, query)


class TestSiblingsQuery(QTestMixin, SimpleTestCase):

    def test_default_query(self):
        query = SiblingsQuery()
        expected = Q(parent=F("parent")) & ~Q(pk=F("pk"))
        self.assertQEqual(expected, query)

    def test_subquery(self):
        query = SiblingsQuery()
        query.to_subquery()
        expected = Q(parent=OuterRef("parent")) & ~Q(pk=OuterRef("pk"))
        self.assertQEqual(expected, query)


class TestLeafNodesQuery(QTestMixin, SimpleTestCase):

    def test_default_query(self):
        query = LeafNodesQuery()
        expected = Q(
            mptt_lft_lt=F("mptt_lft"),
            mptt_rgt_gt=F("mptt_rgt"),
            mptt_tree=F("mptt_tree"),
            mptt_lft=F("mptt_rgt") - 1)
        self.assertQEqual(expected, query)

    def test_default_query_include_self(self):
        query = LeafNodesQuery(include_self=True)
        expected = Q(
            mptt_lft_lte=F("mptt_lft"),
            mptt_rgt_gte=F("mptt_rgt"),
            mptt_tree=F("mptt_tree"),
            mptt_lft=F("mptt_rgt") - 1)
        self.assertQEqual(expected, query)

    def test_subquery(self):
        query = LeafNodesQuery()
        query.to_subquery()
        expected = Q(
            mptt_lft_lt=OuterRef("mptt_lft"),
            mptt_rgt_gt=OuterRef("mptt_rgt"),
            mptt_tree=OuterRef("mptt_tree"),
            mptt_lft=OuterRef("mptt_rgt") - 1)
        self.assertQEqual(expected, query)

    def test_subquery_include_self(self):
        query = LeafNodesQuery(include_self=True)
        query.to_subquery()
        expected = Q(
            mptt_lft_lte=OuterRef("mptt_lft"),
            mptt_rgt_gte=OuterRef("mptt_rgt"),
            mptt_tree=OuterRef("mptt_tree"),
            mptt_lft=OuterRef("mptt_rgt") - 1)
        self.assertQEqual(expected, query)
