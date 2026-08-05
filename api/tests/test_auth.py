from django.urls import reverse
from rest_framework.test import APIClient
import pytest
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
def test_register_user():
    client=APIClient()
    response=client.post(reverse("auth-register"),{
        "username":"testuser",
        "first_name":"test",
        "last_name":"test",
        "email":"test@test.com",
        "password1":"StrongPassword123",
        "password2": "StrongPassword123",
    },format="json",
    )
    assert response.status_code ==201
    assert User.objects.filter(username="testuser").exists()

@pytest.mark.django_db
def test_login():
    User.objects.create_user(
        username="testuser",
        password="StrongPassword123"
    )
    client=APIClient()
    response=client.post(reverse("token-obtain-pair"),{
        "username":"testuser",
        "password":"StrongPassword123",
        },format="json"
    )
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_change_password():
    ...

@pytest.mark.django_db
def test_logout_success():
    user=User.objects.create_user(
        username="testuser",
        password="StrongPassword123"
    )
    refresh=RefreshToken.for_user(user)
    access=str(refresh.access_token)
    client=APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}")
    response=client.post(reverse("logout"),{
        "refresh":str(refresh)
    },
    format="json"
    )
    assert response.status_code == 200
    assert response.data["detail"] == "Logged out successfully."

@pytest.mark.django_db
def test_logout_invalid():
    user = User.objects.create_user(
        username="testuser",
        password="StrongPassword123"
    )
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}")
    response=client.post(reverse("logout"),{
        "refresh":"Invalid-Token"
    },format="json")
    assert response.status_code == 400
    assert response.data["detail"]== "Invalid refresh token."

@pytest.mark.django_db
def test_change_password_success():
    user=User.objects.create_user(
        username="testuser",
        password="OldPassword123"
    )
    refresh=RefreshToken.for_user(user)
    access=str(refresh.access_token)
    client=APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}"
    )
    response=client.post(reverse("change-password"),{
        "old_password":"OldPassword123",
        "new_password":"NewPassword123",
        "new_password2":"NewPassword123"
    },format="json")
    assert response.status_code == 200
    assert response.data["detail"]=="Password changed successfully."
    user.refresh_from_db()
    assert user.check_password("NewPassword123")

@pytest.mark.django_db
def test_change_password_fail():
    user=User.objects.create_user(
        username="testuer",
        password="OldPassword123"
    )
    refresh=RefreshToken.for_user(user)
    access=str(refresh.access_token)
    client=APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}"
    )
    response=client.post(reverse("change-password"),{
        "old_password": "WrongPassword",
        "new_password": "NewPassword123",
        "new_password2": "NewPassword123"
    },format="json")
    assert response.status_code==400
    assert response.data["old_password"][0] == "The current password is not correct."

@pytest.mark.django_db
def test_change_password_weak_password():
    user=User.objects.create_user(
        username="testuer",
        password="OldPassword123"
    )
    refresh=RefreshToken.for_user(user)
    access=str(refresh.access_token)
    client=APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}"
    )
    response=client.post(reverse("change-password"),{
        "old_password": "OldPassword123",
        "new_password": "123",
        "new_password2": "123"
    },format="json")
    assert response.status_code==400

@pytest.mark.django_db
def test_change_password_mismatch():
    user=User.objects.create_user(
        username="testuser",
        password="OldPassword123"
    )
    refresh=RefreshToken.for_user(user)
    access=str(refresh.access_token)
    client=APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}"
    )
    response=client.post(reverse("change-password"),{
        "old_password": "WrongPassword",
        "new_password": "NewPassword123",
        "new_password2": "AnotherPassword123"
    },format="json")

    assert response.status_code == 400
    assert response.data["new_password2"][0]== "Passwords do not match."