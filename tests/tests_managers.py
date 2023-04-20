from django.test import TestCase

from mptt2.enums import Position
from tests.models import SimpleNode


class TestTreeManager(TestCase):

    fixtures = ["simple_nodes.json"]

    def test_insert_without_target(self):
        new_node: SimpleNode = SimpleNode.objects.insert_node(
            node=SimpleNode(),
        )

        self.assertEqual(new_node.mptt_lft, 1)
        self.assertEqual(new_node.mptt_rgt, 2)
        self.assertEqual(new_node.mptt_depth, 0)
        self.assertEqual(new_node.mptt_tree_id, 3)

    def test_insert_last_child(self):
        SimpleNode.objects.insert_node(
            node=SimpleNode(),
            target=SimpleNode.objects.get(pk="14")
        )

        recalculated_tree = SimpleNode.objects.filter(mptt_tree__pk=2)

        self.assertEqual(recalculated_tree.count(), 12)

        self.assertEqual(recalculated_tree[0].pk, 11)
        self.assertEqual(recalculated_tree[0].mptt_lft, 1)
        self.assertEqual(recalculated_tree[0].mptt_rgt, 24)
        self.assertEqual(recalculated_tree[0].mptt_depth, 0)

        self.assertEqual(recalculated_tree[1].pk, 12)
        self.assertEqual(recalculated_tree[1].mptt_lft, 2)
        self.assertEqual(recalculated_tree[1].mptt_rgt, 5)
        self.assertEqual(recalculated_tree[1].mptt_depth, 1)

        self.assertEqual(recalculated_tree[2].pk, 13)
        self.assertEqual(recalculated_tree[2].mptt_lft, 3)
        self.assertEqual(recalculated_tree[2].mptt_rgt, 4)
        self.assertEqual(recalculated_tree[2].mptt_depth, 2)

        self.assertEqual(recalculated_tree[3].pk, 14)
        self.assertEqual(recalculated_tree[3].mptt_lft, 6)
        self.assertEqual(recalculated_tree[3].mptt_rgt, 13)
        self.assertEqual(recalculated_tree[3].mptt_depth, 1)

        self.assertEqual(recalculated_tree[4].pk, 15)
        self.assertEqual(recalculated_tree[4].mptt_lft, 7)
        self.assertEqual(recalculated_tree[4].mptt_rgt, 8)
        self.assertEqual(recalculated_tree[4].mptt_depth, 2)

        self.assertEqual(recalculated_tree[5].pk, 16)
        self.assertEqual(recalculated_tree[5].mptt_lft, 9)
        self.assertEqual(recalculated_tree[5].mptt_rgt, 10)
        self.assertEqual(recalculated_tree[5].mptt_depth, 2)

        self.assertEqual(recalculated_tree[6].pk, 22)
        self.assertEqual(recalculated_tree[6].mptt_lft, 11)
        self.assertEqual(recalculated_tree[6].mptt_rgt, 12)
        self.assertEqual(recalculated_tree[6].mptt_depth, 2)

        self.assertEqual(recalculated_tree[7].pk, 17)
        self.assertEqual(recalculated_tree[7].mptt_lft, 14)
        self.assertEqual(recalculated_tree[7].mptt_rgt, 23)
        self.assertEqual(recalculated_tree[7].mptt_depth, 1)

        self.assertEqual(recalculated_tree[8].pk, 18)
        self.assertEqual(recalculated_tree[8].mptt_lft, 15)
        self.assertEqual(recalculated_tree[8].mptt_rgt, 18)
        self.assertEqual(recalculated_tree[8].mptt_depth, 2)

        self.assertEqual(recalculated_tree[9].pk, 19)
        self.assertEqual(recalculated_tree[9].mptt_lft, 16)
        self.assertEqual(recalculated_tree[9].mptt_rgt, 17)
        self.assertEqual(recalculated_tree[9].mptt_depth, 3)

        self.assertEqual(recalculated_tree[10].pk, 20)
        self.assertEqual(recalculated_tree[10].mptt_lft, 19)
        self.assertEqual(recalculated_tree[10].mptt_rgt, 22)
        self.assertEqual(recalculated_tree[10].mptt_depth, 2)

        self.assertEqual(recalculated_tree[11].pk, 21)
        self.assertEqual(recalculated_tree[11].mptt_lft, 20)
        self.assertEqual(recalculated_tree[11].mptt_rgt, 21)
        self.assertEqual(recalculated_tree[11].mptt_depth, 3)

    def test_insert_first_child(self):
        SimpleNode.objects.insert_node(
            node=SimpleNode(),
            target=SimpleNode.objects.get(pk="14"),
            position=Position.FIRST_CHILD.value
        )

        recalculated_tree = SimpleNode.objects.filter(mptt_tree__pk=2)

        self.assertEqual(recalculated_tree.count(), 12)

        self.assertEqual(recalculated_tree[0].pk, 11)
        self.assertEqual(recalculated_tree[0].mptt_lft, 1)
        self.assertEqual(recalculated_tree[0].mptt_rgt, 24)
        self.assertEqual(recalculated_tree[0].mptt_depth, 0)

        self.assertEqual(recalculated_tree[1].pk, 12)
        self.assertEqual(recalculated_tree[1].mptt_lft, 2)
        self.assertEqual(recalculated_tree[1].mptt_rgt, 5)
        self.assertEqual(recalculated_tree[1].mptt_depth, 1)

        self.assertEqual(recalculated_tree[2].pk, 13)
        self.assertEqual(recalculated_tree[2].mptt_lft, 3)
        self.assertEqual(recalculated_tree[2].mptt_rgt, 4)
        self.assertEqual(recalculated_tree[2].mptt_depth, 2)

        self.assertEqual(recalculated_tree[3].pk, 14)
        self.assertEqual(recalculated_tree[3].mptt_lft, 6)
        self.assertEqual(recalculated_tree[3].mptt_rgt, 13)
        self.assertEqual(recalculated_tree[3].mptt_depth, 1)

        self.assertEqual(recalculated_tree[4].pk, 22)
        self.assertEqual(recalculated_tree[4].mptt_lft, 7)
        self.assertEqual(recalculated_tree[4].mptt_rgt, 8)
        self.assertEqual(recalculated_tree[4].mptt_depth, 2)

        self.assertEqual(recalculated_tree[5].pk, 15)
        self.assertEqual(recalculated_tree[5].mptt_lft, 9)
        self.assertEqual(recalculated_tree[5].mptt_rgt, 10)
        self.assertEqual(recalculated_tree[5].mptt_depth, 2)

        self.assertEqual(recalculated_tree[6].pk, 16)
        self.assertEqual(recalculated_tree[6].mptt_lft, 11)
        self.assertEqual(recalculated_tree[6].mptt_rgt, 12)
        self.assertEqual(recalculated_tree[6].mptt_depth, 2)

        self.assertEqual(recalculated_tree[7].pk, 17)
        self.assertEqual(recalculated_tree[7].mptt_lft, 14)
        self.assertEqual(recalculated_tree[7].mptt_rgt, 23)
        self.assertEqual(recalculated_tree[7].mptt_depth, 1)

        self.assertEqual(recalculated_tree[8].pk, 18)
        self.assertEqual(recalculated_tree[8].mptt_lft, 15)
        self.assertEqual(recalculated_tree[8].mptt_rgt, 18)
        self.assertEqual(recalculated_tree[8].mptt_depth, 2)

        self.assertEqual(recalculated_tree[9].pk, 19)
        self.assertEqual(recalculated_tree[9].mptt_lft, 16)
        self.assertEqual(recalculated_tree[9].mptt_rgt, 17)
        self.assertEqual(recalculated_tree[9].mptt_depth, 3)

        self.assertEqual(recalculated_tree[10].pk, 20)
        self.assertEqual(recalculated_tree[10].mptt_lft, 19)
        self.assertEqual(recalculated_tree[10].mptt_rgt, 22)
        self.assertEqual(recalculated_tree[10].mptt_depth, 2)

        self.assertEqual(recalculated_tree[11].pk, 21)
        self.assertEqual(recalculated_tree[11].mptt_lft, 20)
        self.assertEqual(recalculated_tree[11].mptt_rgt, 21)
        self.assertEqual(recalculated_tree[11].mptt_depth, 3)

    def test_insert_left(self):
        SimpleNode.objects.insert_node(
            node=SimpleNode(),
            target=SimpleNode.objects.get(pk="14"),
            position=Position.LEFT.value
        )

        recalculated_tree = SimpleNode.objects.filter(mptt_tree__pk=2)

        self.assertEqual(recalculated_tree.count(), 12)

        self.assertEqual(recalculated_tree[0].pk, 11)
        self.assertEqual(recalculated_tree[0].mptt_lft, 1)
        self.assertEqual(recalculated_tree[0].mptt_rgt, 24)
        self.assertEqual(recalculated_tree[0].mptt_depth, 0)

        self.assertEqual(recalculated_tree[1].pk, 12)
        self.assertEqual(recalculated_tree[1].mptt_lft, 2)
        self.assertEqual(recalculated_tree[1].mptt_rgt, 5)
        self.assertEqual(recalculated_tree[1].mptt_depth, 1)

        self.assertEqual(recalculated_tree[2].pk, 13)
        self.assertEqual(recalculated_tree[2].mptt_lft, 3)
        self.assertEqual(recalculated_tree[2].mptt_rgt, 4)
        self.assertEqual(recalculated_tree[2].mptt_depth, 2)

        self.assertEqual(recalculated_tree[3].pk, 22)
        self.assertEqual(recalculated_tree[3].mptt_lft, 6)
        self.assertEqual(recalculated_tree[3].mptt_rgt, 7)
        self.assertEqual(recalculated_tree[3].mptt_depth, 1)

        self.assertEqual(recalculated_tree[4].pk, 14)
        self.assertEqual(recalculated_tree[4].mptt_lft, 8)
        self.assertEqual(recalculated_tree[4].mptt_rgt, 13)
        self.assertEqual(recalculated_tree[4].mptt_depth, 1)

        self.assertEqual(recalculated_tree[5].pk, 15)
        self.assertEqual(recalculated_tree[5].mptt_lft, 9)
        self.assertEqual(recalculated_tree[5].mptt_rgt, 10)
        self.assertEqual(recalculated_tree[5].mptt_depth, 2)

        self.assertEqual(recalculated_tree[6].pk, 16)
        self.assertEqual(recalculated_tree[6].mptt_lft, 11)
        self.assertEqual(recalculated_tree[6].mptt_rgt, 12)
        self.assertEqual(recalculated_tree[6].mptt_depth, 2)

        self.assertEqual(recalculated_tree[7].pk, 17)
        self.assertEqual(recalculated_tree[7].mptt_lft, 14)
        self.assertEqual(recalculated_tree[7].mptt_rgt, 23)
        self.assertEqual(recalculated_tree[7].mptt_depth, 1)

        self.assertEqual(recalculated_tree[8].pk, 18)
        self.assertEqual(recalculated_tree[8].mptt_lft, 15)
        self.assertEqual(recalculated_tree[8].mptt_rgt, 18)
        self.assertEqual(recalculated_tree[8].mptt_depth, 2)

        self.assertEqual(recalculated_tree[9].pk, 19)
        self.assertEqual(recalculated_tree[9].mptt_lft, 16)
        self.assertEqual(recalculated_tree[9].mptt_rgt, 17)
        self.assertEqual(recalculated_tree[9].mptt_depth, 3)

        self.assertEqual(recalculated_tree[10].pk, 20)
        self.assertEqual(recalculated_tree[10].mptt_lft, 19)
        self.assertEqual(recalculated_tree[10].mptt_rgt, 22)
        self.assertEqual(recalculated_tree[10].mptt_depth, 2)

        self.assertEqual(recalculated_tree[11].pk, 21)
        self.assertEqual(recalculated_tree[11].mptt_lft, 20)
        self.assertEqual(recalculated_tree[11].mptt_rgt, 21)
        self.assertEqual(recalculated_tree[11].mptt_depth, 3)