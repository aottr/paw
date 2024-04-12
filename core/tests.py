from django.test import TestCase
from django.contrib.auth.models import Group
from django.urls import reverse
from .utils.initial_data import populate_groups
from .utils.general import sainitize_username
from .models import PawUser
from django.conf import settings


class PopulateGroupTestCase(TestCase):
    def setUp(self):
        populate_groups(None, None)

    def test_groups_created(self):
        self.assertEqual(Group.objects.count(), 2)
        self.assertEqual(Group.objects.filter(name="Client").count(), 1)
        self.assertEqual(Group.objects.filter(name="Supporter").count(), 1)

class UsernameSainitizationTestCase(TestCase):
    def test_sainitize_username(self):
        self.assertEqual(sainitize_username("test"), "test")
        self.assertEqual(sainitize_username("test !!"), "test")

class LoginViewTestCase(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "testpassword"
        self.user = PawUser.objects.create_user(username=self.username, password=self.password)

    def test_login_view(self):
        url = reverse("login")
        response = self.client.post(url, {"username": self.username, "password": self.password})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

    def test_login_view_invalid(self):
        url = reverse("login")
        response = self.client.post(url, {"username": self.username, "password": "invalid"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct username and password")
    
    def test_user_language(self):
        url = reverse("home")
        self.client.force_login(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.cookies.load(response.cookies)
        self.assertEqual(self.client.cookies[settings.LANGUAGE_COOKIE_NAME].value, self.user.language)
        self.assertEqual(response.url, reverse("all_tickets"))

class RegisterViewTestCase(TestCase):

    def test_register_view(self):
        url = reverse("register")
        response = self.client.post(url, {"username": "test", "email": "test@example.com", "password": "testtesttesttest", "password_confirm": "testtesttesttest"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))
        self.assertEqual(PawUser.objects.count(), 1)
        user = PawUser.objects.first()
        self.assertEqual(user.username, "test")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testtesttesttest"))
        self.assertEqual(user.groups.count(), 0) # No group assigned, might want to give Client group by default

    def test_register_view_password_too_short(self):
        url = reverse("register")
        response = self.client.post(url, {"username": "test", "email": "test@example.com", "password": "123456789", "password_confirm": "123456789"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password must be at least 10 characters long.")
    
    def test_register_view_password_mismatch(self):
        url = reverse("register")
        response = self.client.post(url, {"username": "test", "email": "test@example.com", "password": "1234567890", "password_confirm": "123456789"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Password and Confirm Password do not match.")

class SettingsViewTestCase(TestCase):

    def test_settings_view(self):
        url = reverse("settings")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "%s?next=%s" % (reverse("login"), reverse("settings")))

        user = PawUser.objects.create_user(username="test", password="testtesttesttest", email="test@example.com")
        self.client.force_login(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Settings")

        response = self.client.post(url, {"language": "fr", "email": "test@example.com"})
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.language, "fr")
        self.client.cookies.load(response.cookies)
        self.assertEqual(self.client.cookies[settings.LANGUAGE_COOKIE_NAME].value, "fr")

        response = self.client.post(url, {"language": "invalid", "email": "test@example.com"})
        self.assertEqual(response.status_code, 200)
        self.client.cookies.load(response.cookies)
        self.assertEqual(self.client.cookies[settings.LANGUAGE_COOKIE_NAME].value, "fr")

        response = self.client.post(url, {"language": "en", "email": "test@example.com"})
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.language, "en")
        self.client.cookies.load(response.cookies)
        self.assertEqual(self.client.cookies[settings.LANGUAGE_COOKIE_NAME].value, "en")
