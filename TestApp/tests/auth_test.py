import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from authtest.models import Profile, Role, UserRole
from authtest.views import base_context

User = get_user_model()

URL_NAMES = {
    "home": "home",
    "register": "register",
    "profile": "profile",
    "assign_role": "assign_role",
    "api_all_users": "api_all_users",
}

VIEWS_MODULE = "authtest.views"

@pytest.fixture
def rf():
    return RequestFactory()

@pytest.fixture
def client_logged(client):
    user = User.objects.create_user(
        username="usertest", email="usertest@example.com", password="password123",
        first_name="John", last_name="Doe"
    )
    Profile.objects.create(user=user, patronymic="Smith")
    client.force_login(user)
    return client, user

@pytest.mark.django_db
def test_register_new_user_success(client):
    url = reverse(URL_NAMES["register"])
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Smith",
        "email": "john.doe@example.com",
        "password": "password123",
        "password2": "password123",
    }
    resp = client.post(url, data)
    assert resp.status_code in (302, 303) 
    u = User.objects.get(email="john.doe@example.com")
    assert u.is_active is True
    prof = Profile.objects.get(user=u)
    assert prof.patronymic == "Smith"
    assert Role.objects.filter(name="user").exists()
    assert UserRole.objects.filter(user=u, role__name="user").exists()

@pytest.mark.django_db
def test_register_existing_inactive_user(client):
    u = User.objects.create_user(username="jane", email="jane@example.com", password="janepass", is_active=False)
    url = reverse(URL_NAMES["register"])
    data = {
        "first_name": "Jane",
        "last_name": "Roe",
        "patronymic": "Petrovna",
        "email": "jane@example.com",
        "password": "newpass",
        "password2": "newpass",
    }
    resp = client.post(url, data)
    assert resp.status_code in (302, 303)
    u.refresh_from_db()
    assert u.is_active is True
    assert u.username == "jane@example.com"
    assert u.first_name == "Jane"
    assert u.last_name == "Roe"
    assert u.check_password("newpass")
    assert Profile.objects.filter(user=u, patronymic="Petrovna").exists()
    assert UserRole.objects.filter(user=u, role__name="user").exists()

@pytest.mark.django_db
def test_register_duplicate_active_user_error(client):
    User.objects.create_user(username="dublicate", email="dublicate@example.com", password="dublicatepass", is_active=True)
    url = reverse(URL_NAMES["register"])
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Smith",
        "email": "dublicate@example.com",
        "password": "dublicatepass1",
        "password2": "dublicatepass1",
    }
    resp = client.post(url, data)
    assert resp.status_code == 200
    assert "уже существует и активен" in resp.content.decode().lower()

@pytest.mark.django_db
def test_register_password_mismatch(client):
    url = reverse(URL_NAMES["register"])
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "patronymic": "Smith",
        "email": "john2@example.com",
        "password": "johnpass1",
        "password2": "johnpass2",
    }
    resp = client.post(url, data)
    assert resp.status_code == 200
    assert "пароли не совпадают" in resp.content.decode().lower()


def _allow_all(user, resource, action):
    return True, 200

def _view_only(user, resource, action):
    if action == "view_profile":
        return True, 200
    if action == "edit_profile":
        return False, 403
    return False, 403

@pytest.mark.django_db
def test_profile_get_ok(monkeypatch, client_logged):
    client, user = client_logged
    monkeypatch.setattr(VIEWS_MODULE + ".check_access", _allow_all, raising=False)

    url = reverse(URL_NAMES["profile"])
    resp = client.get(url)
    assert resp.status_code == 200

    form = resp.context["form"]
    assert form.fields["first_name"].initial == user.first_name
    assert form.fields["last_name"].initial == user.last_name
    assert form.fields["email"].initial == user.email
    assert form.fields["patronymic"].initial == user.profile.patronymic

    assert resp.context["can_edit"] is True


@pytest.mark.django_db
def test_profile_post_update_ok(monkeypatch, client_logged):
    client, user = client_logged
    monkeypatch.setattr(VIEWS_MODULE + ".check_access", _allow_all, raising=False)
    url = reverse(URL_NAMES["profile"])
    payload = {"first_name": "newname", "last_name": "newlastname", "email": "new@example.com", "patronymic": "newpatronymic"}
    resp = client.post(url, payload)
    assert resp.status_code in (302, 303)
    user.refresh_from_db()
    user.profile.refresh_from_db()
    assert user.first_name == "newname"
    assert user.last_name == "newlastname"
    assert user.email == "new@example.com"
    assert user.profile.patronymic == "newpatronymic"

@pytest.mark.django_db
def test_profile_post_forbidden(monkeypatch, client_logged):
    client, user = client_logged
    monkeypatch.setattr(VIEWS_MODULE + ".check_access", _view_only, raising=False)
    url = reverse(URL_NAMES["profile"])
    payload = {"first_name": "Hacker", "last_name": "User", "email": "hack@example.com", "patronymic": "Patronymic"}
    resp = client.post(url, payload)
    assert resp.status_code == 403
    user.refresh_from_db()
    assert user.email != "hack@example.com"

@pytest.mark.django_db
def test_profile_post_delete_account(monkeypatch, client_logged):
    client, user = client_logged
    monkeypatch.setattr(VIEWS_MODULE + ".check_access", _allow_all, raising=False)
    url = reverse(URL_NAMES["profile"])
    resp = client.post(url, {"delete_account": "1"})
    assert resp.status_code in (302, 303)
    user.refresh_from_db()
    assert user.is_active is False


@pytest.mark.django_db
def test_base_context_sets_admin_role(rf):
    user = User.objects.create_user(username="admin", email="admin@example.com", password="adminpass")
    prof = Profile.objects.create(user=user, patronymic="Pat")
    admin_role = Role.objects.create(name="admin")
    UserRole.objects.create(user=user, role=admin_role)

    req = rf.get("/")
    req.user = user
    ctx = base_context(req)
    prof.refresh_from_db()
    assert ctx["profile_obj"] == prof
    assert prof.role == admin_role

@pytest.mark.django_db
def test_base_context_no_profile_returns_none(rf):
    user = User.objects.create_user(username="base", email="base@example.com", password="basepass")
    req = rf.get("/")
    req.user = user
    ctx = base_context(req)
    assert ctx["profile_obj"] is None


@pytest.mark.django_db
def test_all_users_view_unauthorized(client):
    url = reverse(URL_NAMES["api_all_users"])
    resp = client.get(url)
    assert resp.status_code == 401

@pytest.mark.django_db
def test_all_users_view_ok(client):
    u = User.objects.create_user(username="john", email="john@example.com", password="johnpass")
    User.objects.create_user(username="jane", email="jane@example.com", password="janepass")
    User.objects.create_user(username="zoe", email="zoe@example.com", password="zoepass")
    client.force_login(u)
    url = reverse(URL_NAMES["api_all_users"])
    resp = client.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert "users" in data and isinstance(data["users"], list)
    assert len(data["users"]) >= 3


def _assign_allow(user, resource, action):
    if action == "assign_role_page":
        return True, 200
    return False, 403

def _assign_forbid(user, resource, action):
    if action == "assign_role_page":
        return False, 403
    return False, 403

@pytest.mark.django_db
def test_assign_role_page_ok(monkeypatch, client_logged):
    client, _ = client_logged
    monkeypatch.setattr(VIEWS_MODULE + ".check_access", _assign_allow, raising=False)
    url = reverse(URL_NAMES["assign_role"])
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.context["can_assign_role"] is True

@pytest.mark.django_db
def test_assign_role_page_unauthorized(client):
    url = reverse(URL_NAMES["assign_role"])
    resp = client.get(url)
    assert resp.status_code == 401

@pytest.mark.django_db
def test_assign_role_page_forbidden(monkeypatch, client_logged):
    client, _ = client_logged
    monkeypatch.setattr(VIEWS_MODULE + ".check_access", _assign_forbid, raising=False)
    url = reverse(URL_NAMES["assign_role"])
    resp = client.get(url)
    assert resp.status_code == 403
