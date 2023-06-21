
from typing import Dict, List

from django import template
from django.contrib.admin.templatetags.admin_list import result_list

register = template.Library()
register.inclusion_tag('admin/mptt_change_list_results.html')(result_list)

from django.utils.html import escape, mark_safe

from mptt2.models import Node, Tree


class HtmlTag:
    def __init__(self, tag: str, attrs: Dict = None, parent_container=None) -> None:
        self.tag = tag
        self.attrs = attrs if attrs else {}
        self.parent_container = parent_container
        self.children = []

    def append_children(self, tag):
        self.children.append(tag)

    def attrs_to_string(self):
        attrs_str = ""
        for key, value in self.attrs.items():
            attrs_str += f'{key}="{value}"'
        return attrs_str

    def __str__(self):
        content = f"<{self.tag} {self.attrs_to_string()}>"
        for child in self.children:
            content += child.__str__()
        content += f'</{self.tag}>'
        return mark_safe(content)


def build_html_node(node):
    html_node = HtmlTag(tag="div", attrs={"class": "list-group-item"})
    level_string = "".join("-" for _ in range(node.mptt_depth))
    html_node.append_children(f'{level_string} {escape(node)}')
    return html_node

@register.simple_tag
def draggable_tree(nodes):
    html_trees = []
    current_tree: Tree = None
    node: Node = None  # only to provide type hints
    subtree_container = None
    #last_node_container = None

    last_node: Node = None
    last_node_html_container: HtmlTag = None

    html_container_registry = {}

    nodes_list: List[Node] = list(nodes)

    for node in nodes_list:
        
        if node.mptt_tree != current_tree:
            # new tree
            current_tree = node.mptt_tree
            subtree_container = HtmlTag(tag="div", attrs={"id": f'tree-id-{current_tree.pk}', "class": "nested-sortable"})
            html_trees.append(subtree_container)
            last_node = node

        if node.mptt_depth < last_node.mptt_depth:
            # upstairs in the tree
            # TODO: get correct subtree_container for this node
            for x in range(last_node.mptt_depth-node.mptt_depth):
                subtree_container = subtree_container.parent_container
            
        elif node.mptt_depth > last_node.mptt_depth:
            # downstair
            pass


        if node.has_leafs:
            # new subtree
            html_node = build_html_node(node)

            subtree_container.append_children(html_node)

            new_subtree_container = HtmlTag(tag="div", attrs={"class": "list-group nested-sortable"}, parent_container=subtree_container)
            html_node.append_children(new_subtree_container)
            subtree_container = new_subtree_container
        else:
            # leave node
            html_node = build_html_node(node)
            subtree_container.append_children(html_node)

        node.subtree_container = subtree_container

        #     if last_node_container and last_node_container.parent_container:
        #         last_node_container.parent_container.append_children(html_node)
        #     else:
        #         last_node_container = html_node

        # last_node_container = html_node
        last_node = node
                

    content = ""

    for html_content in html_trees:
        content += html_content.__str__()

    return mark_safe(content)