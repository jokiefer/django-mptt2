from django.test import TestCase
from tests.models import SimpleNode

class TestNodeModel(TestCase):
    
    fixtures = ["simple_nodes.json"]

    def test_delete(self):
        node: SimpleNode = SimpleNode.objects.get(pk=4)
        node.delete()

        recalculated_tree = SimpleNode.objects.filter(mptt_tree__pk=1)

        self.assertEqual(recalculated_tree.count(), 3)
        
        self.assertEqual(recalculated_tree[0].mptt_lft, 1)
        self.assertEqual(recalculated_tree[0].mptt_rgt, 6)

        self.assertEqual(recalculated_tree[1].mptt_lft, 2)
        self.assertEqual(recalculated_tree[1].mptt_rgt, 3)

        self.assertEqual(recalculated_tree[2].mptt_lft, 4)
        self.assertEqual(recalculated_tree[2].mptt_rgt, 5)
