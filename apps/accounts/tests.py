from django.test import TestCase, override_settings
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import User


@override_settings(PASSWORD_HASHERS=("django.contrib.auth.hashers.MD5PasswordHasher",))
class UserModelTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email='testemail@gmail.com',
            password='testpassword',
            first_name='test',
            last_name='user',
        )

    def test_user_model(self):
        self.assertEqual(self.user.email, 'testemail@gmail.com')
        self.assertTrue(self.user.check_password('testpassword'))
        self.assertIsNotNone(self.user.profile, msg='Test that the profile was created automatically')
        self.assertEqual(self.user.full_name, 'Test User')

    def test_default_fields(self):
        self.assertEqual(self.user.is_active, True)
        self.assertEqual(self.user.is_superuser, False)
    
    def test_user_instances(self):
        self.assertTrue(isinstance(self.user, User))
        self.assertEqual(settings.AUTH_USER_MODEL, 'accounts.User')


@override_settings(PASSWORD_HASHERS=("django.contrib.auth.hashers.MD5PasswordHasher",),
                   ACCOUNT_EMAIL_VERIFICATION="optional")
class UserAPITest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email='testemail@gmail.com',
            password='testpassword',
            first_name='test',
            last_name='user',
        )

    def setUp(self) -> None:
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_user(self):
        """create user"""
        url = reverse_lazy('rest_register')
        data = {
            "email": "testuser@test.com",
            "password": "testpassword123",
            "first_name": "string",
            "last_name": "last",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data["user"])
        self.assertIsNotNone(response.data["user"]["profile"])
        self.assertIsNotNone(response.data["access"])
        self.assertIsNotNone(response.data["refresh"])
        data = response.data["user"]
        self.assertEqual(data["first_name"], "string")
        self.assertEqual(data["last_name"], "last")
        self.assertEqual(data["email"], "testuser@test.com")

    def test_create_with_missing_field(self):
        """create user with missing required fields"""
        url = reverse_lazy('rest_register')
        data = {
            "email": "testuser@test.com",
            "password": "testpassword123",
            "first_name": "string",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["data"]['last_name'][0], "This field is required.")
    
    def test_user_login(self):
        """user login"""
        url = reverse_lazy("rest_login")
        data = {
            "email": 'testemail@gmail.com',
            "password": "testpassword"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["user"])
        data = response.data["user"]
        self.assertEqual(data["email"], "testemail@gmail.com")
        self.assertEqual(data["first_name"], "test")
        self.assertEqual(data["last_name"], "user")
    
    def test_user_login_wrong_password(self):
        """test response when user login with wrong password"""
        url = reverse_lazy("rest_login")
        data = {
            "email": "testuser@test.com",
            "password": "wrongpassword123"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["data"]["non_field_errors"][0],
            "Unable to log in with provided credentials."
            )
    
    def test_get_user_info(self):
        """Get user info"""
        url = reverse_lazy("rest_user_details")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)
        data = response.data
        self.assertEqual(data["email"], "testemail@gmail.com")
        self.assertEqual(data["first_name"], "test")
        self.assertEqual(data["last_name"], "user")
        self.assertIsNotNone(data["profile"])
    
    def test_update_user_info(self):
        """update user info and profile"""
        url = reverse_lazy("rest_user_details")
        data = {
            "first_name": "Changed",
            "profile": {
                "state": "test state"
            }
        }
        response = self.client.patch(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data)
        data = response.data
        self.assertEqual(data["first_name"], "Changed")
        self.assertEqual(data["last_name"], "user")
        # self.assertEqual(self.user.profile.state, "test state")

    def test_update_user_info_wrong_method(self):
        url = reverse_lazy("rest_user_details")
        data = {
            "first_name": "Changed",
            "last_name": "test",
            "profile": {
                "state": "test state"
            }
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            response.data["message"],
            "Method not allowed: PUT. Only `PATCH`"
        )
    
    def test_update_user_email(self):
        url = reverse_lazy("rest_user_details")
        data = {
            "email": "fakeemail@gmail.com"
        }
        response = self.client.patch(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "testemail@gmail.com", "can't update email")
    
    def test_update_readonly_fields(self):
        url = reverse_lazy("rest_user_details")
        data = {
            "is_active": False
        }
        response = self.client.patch(url, data, format="json")
        self.user.refresh_from_db()
        self.assertEqual(self.user.is_active, True)
    
    def test_user_change_password(self):
        """Test the user change password endpoint"""
        url = reverse_lazy('rest_password_change')
        data = {
            'new_password1': 'testpassword2',
            'new_password2': 'testpassword2',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'New password has been saved.')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('testpassword2'))
        """login with new password"""
        url = reverse_lazy('rest_login')
        data = {
            "email": "testemail@gmail.com",
            "password": "testpassword2",
        }
        response = self.client.post(url, data, format="json")
        user_data = response.data["user"]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user_data['email'], "testemail@gmail.com")

