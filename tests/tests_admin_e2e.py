import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from playwright.sync_api import sync_playwright


class TestDragAndDrop(StaticLiveServerTestCase):

    fixtures = ["auth.json", "simple_nodes.json", "other_nodes.json"]

    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        super().setUp()
        client = Client()
        client.login(username="superuser", password='12345678') #Native django test client
        morsel = client.cookies['sessionid']

        cookie_dict = {
            "name": morsel.key,
            "value": morsel.value,
            "url": self.live_server_url,
        }
        
        self.context = self.browser.new_context()
        self.context.add_cookies([cookie_dict])
        

    def test_drag_node_five_to_node_three(self):
        # just a simple e2e test to figure out static sortablejs lib is provided as static file and drag and drop is principle working
        page = self.context.new_page()
        page.goto(f"{self.live_server_url}/admin/tests/simplenode/")

        page.wait_for_selector('text=Select simple node to change')

        node_five = page.locator('li[data-target-id="5"]')

        node_three = page.locator('li[data-target-id="2"]')

        node_five.drag_to(target=node_three, target_position={"x": 0, "y": 1}, )

        page.wait_for_selector('text=pk 5 | tree 1 | lft 2 | rgt 3')
