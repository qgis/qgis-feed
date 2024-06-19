from django.test import TestCase
from django.test import Client

class LoginTestCase(TestCase):
    """
    Test the login feature
    """
    fixtures = ['qgisfeed.json', 'users.json']

    def setUp(self):
        self.client = Client()

    def test_valid_login(self):
        response = self.client.login(username='admin', password='admin')
        self.assertTrue(response)

    def test_invalid_login(self):
        response = self.client.login(username='admin', password='wrongpassword')
        self.assertFalse(response)