import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from authtest.models import Role, Permission, Resource, UserRole


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_role(db):
    return Role.objects.create(name="admin")


@pytest.fixture
def non_admin_role(db):
    return Role.objects.create(name="user")


@pytest.fixture
def admin_user(db, admin_role):
    user = User.objects.create_user(username="admin", password="adminpass", email="admin@example.com")
    UserRole.objects.create(user=user, role=admin_role)
    return user


@pytest.fixture
def regular_user(db, non_admin_role):
    user = User.objects.create_user(username="john", password="johnpass", email="john@example.com")
    UserRole.objects.create(user=user, role=non_admin_role)
    return user


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def user_client(api_client, regular_user):
    api_client.force_authenticate(user=regular_user)
    return api_client


@pytest.fixture
def sample_role(db):
    return Role.objects.create(name="manager")


@pytest.fixture
def sample_permission(db):
    return Permission.objects.create(code="view_dashboard", description="Can view dashboard")


@pytest.fixture
def sample_resource(db):
    return Resource.objects.create(name="dashboard", description="Main dashboard")
