from django.test import TestCase
from django.urls import reverse

class HomePageTestCase(TestCase):
    """
    Test home page web version
    """
    fixtures = ['qgisfeed.json', 'users.json']

    def setUp(self):
        pass

    def test_authenticated_user_access(self):
        self.client.login(username='admin', password='admin')

        # Access the all view after logging in
        response = self.client.get(reverse('all'))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'feeds/feed_home_page.html')
        self.assertTrue('form' in response.context)


    def test_unauthenticated_user_access(self):
        # Access the all view without logging in
        response = self.client.get(reverse('all'))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'feeds/feed_home_page.html')
        self.assertTrue('form' in response.context)

    def test_feeds_list_filtering(self):
        # Test filter homepage feeds

        data = {
            'lang': 'en',
            'publish_from': '2023-12-31',
        }
        response = self.client.get(reverse('all'), data)

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'feeds/feed_home_page.html')
        self.assertTrue('form' in response.context)

