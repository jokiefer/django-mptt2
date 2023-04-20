from django.test import TestCase

from tests.models import SimpleNode


class TestNodeModel(TestCase):

    fixtures = ["simple_nodes.json"]

    def test_delete(self):
        node: SimpleNode = SimpleNode.objects.get(pk=18)
        node.delete()

        recalculated_tree = SimpleNode.objects.filter(mptt_tree__pk=2)

        self.assertEqual(recalculated_tree.count(), 9)

        self.assertEqual(recalculated_tree[0].mptt_lft, 1)
        self.assertEqual(recalculated_tree[0].mptt_rgt, 18)

        self.assertEqual(recalculated_tree[1].mptt_lft, 2)
        self.assertEqual(recalculated_tree[1].mptt_rgt, 5)

        self.assertEqual(recalculated_tree[2].mptt_lft, 3)
        self.assertEqual(recalculated_tree[2].mptt_rgt, 4)

        self.assertEqual(recalculated_tree[3].mptt_lft, 6)
        self.assertEqual(recalculated_tree[3].mptt_rgt, 11)

        self.assertEqual(recalculated_tree[4].mptt_lft, 7)
        self.assertEqual(recalculated_tree[4].mptt_rgt, 8)

        self.assertEqual(recalculated_tree[5].mptt_lft, 9)
        self.assertEqual(recalculated_tree[5].mptt_rgt, 10)

        self.assertEqual(recalculated_tree[6].mptt_lft, 12)
        self.assertEqual(recalculated_tree[6].mptt_rgt, 17)

        self.assertEqual(recalculated_tree[7].mptt_lft, 13)
        self.assertEqual(recalculated_tree[7].mptt_rgt, 16)

        self.assertEqual(recalculated_tree[8].mptt_lft, 14)
        self.assertEqual(recalculated_tree[8].mptt_rgt, 15)
