from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient


class UserAPITests(TestCase):
    def setUp(self):
        User = get_user_model()

        seller_group, _ = Group.objects.get_or_create(
            name="Seller"
        )

        manager_group, _ = Group.objects.get_or_create(
            name="Manager"
        )

        self.seller = User.objects.create_user(
            username="seller",
            password="StrongPass123!",
            account_type="basic"
        )
        self.seller.groups.add(seller_group)

        self.manager = User.objects.create_user(
            username="manager",
            password="StrongPass123!"
        )
        self.manager.groups.add(manager_group)

        self.client = APIClient()

    def test_registration(self):
        response = self.client.post(
            "/api/users/register/",
            {
                "username": "new_seller",
                "email": "new@example.com",
                "password": "StrongPass123!"
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

    def test_me_requires_authentication(self):
        response = self.client.get(
            "/api/users/me/"
        )

        self.assertEqual(response.status_code, 401)

    def test_user_can_view_profile(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.get(
            "/api/users/me/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["username"],
            "seller"
        )

    def test_premium_purchase(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.post(
            "/api/users/premium/purchase/"
        )

        self.assertEqual(response.status_code, 201)

        self.seller.refresh_from_db()

        self.assertEqual(
            self.seller.account_type,
            "premium"
        )

    def test_cannot_purchase_premium_twice(self):
        self.client.force_authenticate(user=self.seller)

        self.client.post(
            "/api/users/premium/purchase/"
        )

        response = self.client.post(
            "/api/users/premium/purchase/"
        )

        self.assertEqual(response.status_code, 400)

    def test_seller_cannot_block_users(self):
        self.client.force_authenticate(user=self.seller)

        response = self.client.patch(
            f"/api/users/manager/users/{self.manager.id}/status/",
            {"is_active": False},
            format="json"
        )

        self.assertEqual(response.status_code, 403)

    def test_manager_can_block_seller(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.patch(
            f"/api/users/manager/users/{self.seller.id}/status/",
            {"is_active": False},
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        self.seller.refresh_from_db()

        self.assertFalse(self.seller.is_active)
