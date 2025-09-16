import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from authtest.models import Role, Permission, Resource, UserRole, RolePermission, Profile 


@pytest.mark.django_db
class TestPermissions:
    @pytest.mark.parametrize("name", [
        "role-list",
        "permission-list",
        "resource-list",
        "userrole-list",
        "rolepermission-list",
    ])
    def test_non_admin_forbidden_on_protected_viewsets(self, user_client, name):
        url = reverse(name)
        resp = user_client.get(url)
        assert resp.status_code == 403

    @pytest.mark.parametrize("name,payload,model,field", [
        ("role-list", {"name": "auditor", "description": ""}, Role, "name"),
        ("permission-list", {"code": "edit_user", "description": ""}, Permission, "code"),
        ("resource-list", {"name": "users", "description": ""}, Resource, "name"),
    ])
    def test_admin_can_create_basic_entities(self, admin_client, name, payload, model, field):
        url = reverse(name)
        resp = admin_client.post(url, payload, format="json")
        assert resp.status_code == 201
        assert model.objects.filter(**{field: payload[field]}).exists()


@pytest.mark.django_db
class TestAssignRole:
    def test_assign_role_success(self, admin_client, sample_role):
        target = User.objects.create_user(username="alice", password="alicepass", email="alice@example.com")

        url = reverse("userrole-assign-role")
        resp = admin_client.post(url, {"user_id": target.id, "role_id": sample_role.id}, format="json")
        assert resp.status_code == 200
        assert UserRole.objects.filter(user=target, role=sample_role).exists()

    def test_assign_role_missing_params(self, admin_client, sample_role):
        url = reverse("userrole-assign-role")
        resp = admin_client.post(url, {"user_id": None, "role_id": sample_role.id}, format="json")
        assert resp.status_code == 400
        assert "обязательны" in resp.json().get("error", "").lower()

    def test_assign_role_not_found(self, admin_client):
        url = reverse("userrole-assign-role")
        resp = admin_client.post(url, {"user_id": 999999, "role_id": 888888}, format="json")
        assert resp.status_code == 404
        assert "не найдены" in resp.json().get("error", "").lower()


@pytest.mark.django_db
class TestAssignPermission:
    def test_assign_permission_success(
        self, admin_client, sample_role, sample_permission, sample_resource
    ):

        url = reverse("rolepermission-assign-permission")
        payload = {
            "role_id": sample_role.id,
            "permission_id": sample_permission.id,
            "resource_id": sample_resource.id,
        }
        resp = admin_client.post(url, payload, format="json")
        assert resp.status_code == 200
        assert RolePermission.objects.filter(
            role=sample_role, permission=sample_permission, resource=sample_resource
        ).exists()

    def test_assign_permission_missing_fields(self, admin_client, sample_role, sample_permission):
        url = reverse("rolepermission-assign-permission")
        resp = admin_client.post(url, {"role_id": sample_role.id, "permission_id": sample_permission.id}, format="json")
        assert resp.status_code == 400
        assert "обязательны" in resp.json().get("error", "").lower()

    def test_assign_permission_not_found(self, admin_client):
        url = reverse("rolepermission-assign-permission")
        resp = admin_client.post(url, {"role_id": 1, "permission_id": 2, "resource_id": 3}, format="json")
        assert resp.status_code == 404
        assert "не найдены" in resp.json().get("error", "").lower()


@pytest.mark.django_db
class TestModels:
    def test_profile_is_admin_true_false(self, db):
        role_admin = Role.objects.create(name="admin")
        role_user = Role.objects.create(name="user")

        u1 = User.objects.create_user(username="aadmin", password="adminpass")
        u2 = User.objects.create_user(username="user", password="userpass")

        p1 = Profile.objects.create(user=u1, role=role_admin, patronymic="adminpatron")
        p2 = Profile.objects.create(user=u2, role=role_user, patronymic="userpatron")

        assert p1.is_admin() is True
        assert p2.is_admin() is False
