from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class RegistrationTests(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'secret'}
        User.objects.create_user(**self.credentials)

    def testLogin(self):
        response = self.client.post(reverse('registration:login'), self.credentials, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def testLogout(self):
        self.testLogin()
        response = self.client.post(reverse('registration:logout'), {}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def testSignup(self):
        username = "testuser2"
        password = "483n5f7857bf"
        email = "aaa@gmail.com"
        response = self.client.post(reverse('registration:signup'), {'username': username, 'password1': password, 'password2': password, 'email':email}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username=username).exists())

        response = self.client.post(reverse('registration:logout'), {}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

        response = self.client.post(reverse('registration:login'), {'username': username, 'password': password}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def testSignUpErrors(self):

        username = "testuser2"
        password = "483n5f7857bf"
        email = "aaa@gmail.com"
        response = self.client.post(reverse('registration:signup'), {'username': username, 'password1': password, 'password2': password[:-1], 'email':email}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords do not match")
        self.assertFalse(User.objects.filter(username=username).exists())

        response = self.client.post(reverse('registration:signup'), {'username': "%", 'password1': password, 'password2': password, 'email':email}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")
        self.assertFalse(User.objects.filter(username=username).exists())

    def testLogInErrors(self):

        username = "testuser2"
        password = "483n5f7857bf"
        email = "aaa@gmail.com"
        response = self.client.post(reverse('registration:login'), {'username': username, 'password': password}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid username or password")
