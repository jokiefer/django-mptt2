
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase


class TestMpttAdminListView(TestCase):

    fixtures = ["auth.json", "simple_nodes.json", "other_nodes.json"]

    base_url = "/admin/tests/othernode/"
    delete_link = '<a class="deletelink" href="/admin/tests/othernode/1/delete/">Delete</a>'
    insert_link = '<a href="insert_at/" class="addlink">insert node</a>'
    move_link = '<a href="/admin/tests/othernode/1/move_to/">&#8982; Move</a>'
    template = "admin/mptt_change_list.html"
    link_column = '<a href="/admin/tests/othernode/2/change/">&nbsp;&nbsp;&#x2022; pk 2 | tree 1 | lft 2 | rgt 3</a>'
    view_permission = "view_othernode"
    add_permission = "add_othernode"
    change_permission = "change_othernode"
    delete_permission = "delete_othernode"


    def setUp(self):
        self.client = Client()
        self.simple_user = get_user_model().objects.get(username='simpleuser')
        self.client.force_login(self.simple_user)

    def test_without_permissions(self): 
        self.response = self.client.get(self.base_url)
        self.assertEqual(self.response.status_code, 403)
        self.assertTemplateUsed(self.template)

    def test_with_view_permissions(self):
        self.simple_user.user_permissions.add(Permission.objects.get(codename=self.view_permission))
        self.response = self.client.get(self.base_url)

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.template)

        # proof tree node string
        self.assertContains(self.response, self.link_column)
        # proof perm depending buttons
        self.assertNotContains(self.response, self.delete_link)
        self.assertNotContains(self.response, self.insert_link)
        if self.move_link:
            self.assertNotContains(self.response, self.move_link)

    def test_with_add_permissions(self):
        self.simple_user.user_permissions.add(Permission.objects.get(codename=self.view_permission))
        self.simple_user.user_permissions.add(Permission.objects.get(codename=self.add_permission))
        self.response = self.client.get(self.base_url)

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.template)

        self.assertNotContains(self.response, self.delete_link)
        self.assertContains(self.response, self.insert_link)
        if self.move_link:
            self.assertNotContains(self.response, self.move_link)
    
    def test_with_delete_permissions(self):
        self.simple_user.user_permissions.add(Permission.objects.get(codename=self.view_permission))
        self.simple_user.user_permissions.add(Permission.objects.get(codename=self.delete_permission))
        self.response = self.client.get(self.base_url)

        self.assertTemplateUsed(self.template)

        self.assertContains(self.response, self.delete_link)
        self.assertNotContains(self.response, self.insert_link)
        if self.move_link:
            self.assertNotContains(self.response, self.move_link)

    def test_with_change_permissions(self):
        self.simple_user.user_permissions.add(Permission.objects.get(codename=self.view_permission))
        self.simple_user.user_permissions.add(Permission.objects.get(codename=self.change_permission))
        self.response = self.client.get(self.base_url)
        self.assertTemplateUsed(self.template)        

        self.assertNotContains(self.response, self.delete_link)
        self.assertNotContains(self.response, self.insert_link)
        if self.move_link:
            self.assertContains(self.response, self.move_link)



class TestMpttDraggableListView(TestMpttAdminListView):

    base_url = "/admin/tests/simplenode/"
    template = "admin/mptt_draggable_change_list.html"
    link_column = 'pk 1 | tree 1 | lft 1 | rgt 12 '
    move_link = None
    delete_link = '<a class="deletelink" href="/admin/tests/simplenode/1/delete/">delete</a>'
    view_permission = "view_simplenode"
    add_permission = "add_simplenode"
    change_permission = "change_simplenode"
    delete_permission = "delete_simplenode"


class TestInsertFormView(TestCase):
    fixtures = ["auth.json", "simple_nodes.json", "other_nodes.json"]

    base_url = "/admin/tests/othernode/insert_at/"
    add_permission = "add_othernode"


    def setUp(self):
        super().setUp()
        self.client = Client()
        self.simple_user = get_user_model().objects.get(username='simpleuser')
        self.client.force_login(self.simple_user)
    
    def test_get_without_permissions(self): 
        self.response = self.client.get(self.base_url)
        self.assertEqual(self.response.status_code, 403)

    def test_get_with_permissions(self):
        self.simple_user.user_permissions.add(Permission.objects.get(codename=self.add_permission))
        self.response = self.client.get(self.base_url)
        self.assertEqual(self.response.status_code, 200)

    def test_post_without_permissions(self):
        self.response = self.client.post(self.base_url, data={})
        self.assertEqual(self.response.status_code, 403)

    def test_post_with_permissions(self):
        self.simple_user.user_permissions.add(Permission.objects.get(codename=self.add_permission))
        self.response = self.client.post(self.base_url, data={"title": "new node","target": "5", "position": "first-child"}, follow=True)
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, '<li class="success">The other node “pk 22 | tree 1 | lft 8 | rgt 9” was added successfully.</li>')


class TestMoveFormView(TestCase):
    fixtures = ["auth.json", "simple_nodes.json", "other_nodes.json"]

    base_url = "/admin/tests/othernode/3/move_to/"
    change_permission = "change_othernode"


    def setUp(self):
        super().setUp()
        self.client = Client()
        self.simple_user = get_user_model().objects.get(username='simpleuser')
        self.client.force_login(self.simple_user)
    
    def test_get_without_permissions(self): 
        self.response = self.client.get(self.base_url)
        self.assertEqual(self.response.status_code, 403)

    def test_get_with_permissions(self):
        self.simple_user.user_permissions.add(Permission.objects.get(codename=self.change_permission))
        self.response = self.client.get(self.base_url)
        self.assertEqual(self.response.status_code, 200)

    def test_post_without_permissions(self):
        self.response = self.client.post(self.base_url, data={})
        self.assertEqual(self.response.status_code, 403)

    def test_post_with_permissions(self):
        self.simple_user.user_permissions.add(Permission.objects.get(codename=self.change_permission))
        self.response = self.client.post(self.base_url, data={"target": "5", "position": "first-child"}, follow=True)
        self.assertEqual(self.response.status_code, 200)
        self.assertContains(self.response, '<li class="success">The other node “<a href="/admin/tests/othernode/3/move_to/">pk 3 | tree 1 | lft 6 | rgt 7</a>” was changed successfully.</li>')

