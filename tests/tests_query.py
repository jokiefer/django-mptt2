from django.test import SimpleTestCase

from mptt2.query import ParentQuery


from django.db.models.query_utils import Q
from django.db.models.expressions import F, OuterRef, Subquery

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
    
        
    def test_parent_query(self):
        query = ParentQuery()
        expected = Q(
            mptt_lft=F("mptt_lft") - 1,
            mptt_rgt=F("mptt_rgt") + 1,
            tree_id=F("tree_id"),)
        self.assertQEqual(expected, query)


    def test_parent_subquery(self):
        query = ParentQuery()
        query.to_subquery()
        expected = Q(
            mptt_lft=OuterRef("mptt_lft") - 1,
            mptt_rgt=OuterRef("mptt_rgt") + 1,
            tree_id=OuterRef("tree_id"),)
        self.assertQEqual(expected, query)