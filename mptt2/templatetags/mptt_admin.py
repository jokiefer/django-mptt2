
from typing import Dict, List

from django import template
from django.contrib.admin.templatetags.admin_list import result_list
from django.urls import reverse
from django.utils.html import escape, mark_safe
from django.utils.translation import gettext_lazy as _

from mptt2.models import Node, Tree


register = template.Library()
register.inclusion_tag('admin/mptt_change_list_results.html')(result_list)




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
            attrs_str += f'{" " if attrs_str else ""}{key}="{value}"'
        return attrs_str

    def __str__(self):
        content = f"<{self.tag} {self.attrs_to_string()}>"
        for child in self.children:
            content += child.__str__()
        content += f'</{self.tag}>'
        return mark_safe(content)

def build_delete_node_button(node, request):
    # FIXME: for now we can't check object base permissions with has_perm('perm', node), cause django's default auth backend will always fail if obj!= None.
    if request.user.has_perm(f"{node.__class__._meta.app_label}.delete_{node._meta.model_name.lower()}"):
        delete_link = HtmlTag(
            tag="a", 
            attrs={
                "class": "deletelink",
                "href": reverse(f"admin:{node._meta.app_label}_{node._meta.model_name}_delete", args=(node.id,))
            }
        )
        delete_link.append_children(
            _("delete")
        )
        return delete_link
    return ""


def build_html_node(node, request):
    html_node = HtmlTag(
        tag="li", 
        attrs={
            #"class": "list-group-item",
            "data-target-id": node.pk,
        }
    )
    html_node.append_children(f'{escape(node)} {mark_safe(build_delete_node_button(node, request))}')
    return html_node

@register.simple_tag(takes_context=True)
def draggable_tree(context, nodes):
    html_trees = []
    current_tree: Tree = None
    node: Node = None  # only to provide type hints
    subtree_container = None

    last_node: Node = None


    nodes_list: List[Node] = list(nodes)

    for node in nodes_list:
        
        if node.mptt_tree != current_tree:
            # new tree
            current_tree = node.mptt_tree
            subtree_container = HtmlTag(
                tag="ul", 
                attrs={
                    "id": f'tree-id-{current_tree.pk}', 
                    "class": "nested-sortable",
                    "data-target-id": node.pk,
                    }
                )
            html_trees.append(subtree_container)
            last_node = node

        if node.mptt_depth < last_node.mptt_depth:
            # upstairs in the tree
            for _ in range(last_node.mptt_depth-node.mptt_depth):
                subtree_container = subtree_container.parent_container
            
        if node.has_leafs:
            # new subtree
            html_node = build_html_node(node, context.request)

            subtree_container.append_children(html_node)

            new_subtree_container = HtmlTag(
                tag="ul", 
                attrs={
                    "class": "nested-sortable",
                    "data-target-id": node.pk,
                }, 
                parent_container=subtree_container
            )
            html_node.append_children(new_subtree_container)
            subtree_container = new_subtree_container
        else:
            # leave node
            html_node = build_html_node(node, context.request)
            new_subtree_container = HtmlTag(
                tag="ul", 
                attrs={
                    "class": "nested-sortable",
                    "data-target-id": node.pk,
                }, 
                parent_container=subtree_container)
            html_node.append_children(new_subtree_container)
            subtree_container.append_children(html_node)

        node.subtree_container = subtree_container

        last_node = node
                

    content = ""

    for html_content in html_trees:
        content += html_content.__str__()

    return mark_safe(content)