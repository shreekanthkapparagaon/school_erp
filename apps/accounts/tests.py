from django.test import TestCase
from django.urls import reverse

from .models import User


class AccountsSmokeTests(TestCase):
    PASSWORD = "StrongPass123!"

    def setUp(self):
        self.user = User.objects.create_user(
            email="admin@example.com",
            password=self.PASSWORD,
            role=User.Role.MANAGER,
        )

    def test_user_creation(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.email, "admin@example.com")

    def test_login(self):
        self.assertTrue(
            self.client.login(
                email="admin@example.com",
                password=self.PASSWORD,
            )
        )

    def test_home_page(self):
        self.client.force_login(self.user)

        response = self.client.get("/")

        self.assertIn(
            response.status_code,
            [200, 302],
        )