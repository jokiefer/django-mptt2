
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase


class AdminTestBasicClass(TestCase):
    fixtures = ["auth.json", "simple_nodes.json", "other_nodes.json"]

    def setUp(self):
        self.client = Client()
        #self.client.login(username="fred", password="secret")
        self.simple_user = get_user_model().objects.get(username='simpleuser')
        self.super_user = get_user_model().objects.get(username='superuser')



class TestMpttAdminList(AdminTestBasicClass):

    base_url = "/admin/tests/othernode/"
    delete_link = '<a class="deletelink" href="/admin/tests/othernode/1/delete/">Delete</a>'
    insert_link = '<a href="insert_at/" class="addlink">insert node</a>'
    move_link = '<a href="/admin/tests/othernode/1/move_to/">&#8982; Move</a>'
    template = "admin/mptt_change_list.html"
    link_column = '<a href="/admin/tests/othernode/2/change/">&nbsp;&nbsp;&#x2022; pk 2 | tree 1 | lft 2 | rgt 3</a>'

    def test_mptt_admin_list(self):
        self.client.force_login(self.simple_user)
        
        # without view permission
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(self.template)

        # with view permission
        self.simple_user.user_permissions.add(Permission.objects.get(codename="view_othernode"))
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.template)

        # proof tree node string
        self.assertContains(response, self.link_column)
        # proof perm depending buttons
        self.assertNotContains(response, self.delete_link)
        self.assertNotContains(response, self.insert_link)
        self.assertNotContains(response, self.move_link)

        # with add permission
        self.simple_user.user_permissions.add(Permission.objects.get(codename="add_othernode"))
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(self.template)

        self.assertNotContains(response, self.delete_link)
        self.assertContains(response, self.insert_link)
        self.assertNotContains(response, self.move_link)

        # with delete permission
        self.simple_user.user_permissions.add(Permission.objects.get(codename="delete_othernode"))
        response = self.client.get(self.base_url)
        self.assertTemplateUsed(self.template)

        self.assertContains(response, self.delete_link)
        self.assertContains(response, self.insert_link)
        self.assertNotContains(response, self.move_link)

        # with change permission
        self.simple_user.user_permissions.add(Permission.objects.get(codename="change_othernode"))
        response = self.client.get(self.base_url)
        self.assertTemplateUsed(self.template)        

        self.assertContains(response, self.delete_link)
        self.assertContains(response, self.insert_link)
        self.assertContains(response, self.move_link)



class TestMpttDraggableList(AdminTestBasicClass):

    def test_mptt_draggable_admin_list(self):
        self.client.force_login(self.simple_user)

        response = self.client.get("/admin/tests/simplenode/")
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed("admin/mptt_draggable_change_list.html")
