from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver


class TestDragAndDrop(StaticLiveServerTestCase):

    fixtures = ["auth.json", "simple_nodes.json", "other_nodes.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_drag_node_five_to_node_three(self):
        self.client.login(username="simpleuser", password='12345678') #Native django test client
        cookie = self.client.cookies['sessionid']
        self.selenium.add_cookie({'name': 'sessionid', 'value': cookie.value, 'secure': False, 'path': '/'})
        self.selenium.get(f"{self.live_server_url}/admin/tests/simplenode/")
        
        node_five = self.selenium.find_element(By.CSS_SELECTOR, '[data-target-id="5"]')


        node_three = self.selenium.find_element(By.CSS_SELECTOR, '[data-target-id="3"]')

        # Actions act=new Actions(driver);
        # act.dragAndDrop(From, To).build().perform();							

        # username_input = self.selenium.find_element(By.NAME, "username")
        # username_input.send_keys("myuser")
        # password_input = self.selenium.find_element(By.NAME, "password")
        # password_input.send_keys("secret")
        # self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()