from django.test import TestCase
from django.contrib.auth.models import User

class RegistrationTests(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.credentials)

    def testLogin(self):
        response = self.client.post('/login/', self.credentials, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_active)

    def testSignup(self):
        pass
