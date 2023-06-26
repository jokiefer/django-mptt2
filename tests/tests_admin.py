
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

    def test_mptt_admin_list(self):
        self.client.force_login(self.simple_user)
        
        # without view permission
        response = self.client.get("/admin/tests/othernode/")
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed("admin/mptt_change_list.html")

        # with view permission
        self.simple_user.user_permissions.add(Permission.objects.get(codename="view_othernode"))
        response = self.client.get("/admin/tests/othernode/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("admin/mptt_change_list.html")

        # proof tree node string
        self.assertContains(response, '<a href="/admin/tests/othernode/2/change/">&nbsp;&nbsp;&#x2022; pk 2 | tree 1 | lft 2 | rgt 3</a>')
        # proof perm depending buttons
        self.assertNotContains(response, '<td class="field-delete_link"><a class="deletelink" href="/admin/tests/othernode/1/delete/">Delete</a></td>')
        self.assertNotContains(response, '<a href="insert_at/" class="addlink">insert node</a>')

        # with add permission
        self.simple_user.user_permissions.add(Permission.objects.get(codename="add_othernode"))
        response = self.client.get("/admin/tests/othernode/")

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("admin/mptt_change_list.html")

        self.assertNotContains(response, '<td class="field-delete_link"><a class="deletelink" href="/admin/tests/othernode/1/delete/">Delete</a></td>')
        self.assertContains(response, '<a href="insert_at/" class="addlink">insert node</a>')

        # with delete permission
        self.simple_user.user_permissions.add(Permission.objects.get(codename="delete_othernode"))
        self.assertContains(response, '<td class="field-delete_link"><a class="deletelink" href="/admin/tests/othernode/1/delete/">Delete</a></td>')
        self.assertContains(response, '<a href="insert_at/" class="addlink">insert node</a>')



class TestMpttDraggableList(AdminTestBasicClass):

    def test_mptt_draggable_admin_list(self):
        self.client.force_login(self.simple_user)

        response = self.client.get("/admin/tests/simplenode/")
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed("admin/mptt_draggable_change_list.html")
