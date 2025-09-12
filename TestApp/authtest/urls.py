from django.urls import path, include
from .views import register, profile_view, all_users_view, assign_role_page
from .api import ProfileMeView
from .api import ProfileMeView
from .rbac_api import (
    RoleViewSet,
    PermissionViewSet,
    ResourceViewSet,
    UserRoleViewSet,
    RolePermissionViewSet,
)
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path("", TemplateView.as_view(template_name="base.html"), name="home"),
    path("register/", register, name="register"),
    path("profile/", profile_view, name="profile"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/user/", ProfileMeView.as_view(), name="api_user_me"),
    path("assign-role/", assign_role_page, name="assign_role"),
    path("api/all-users/", all_users_view, name="api_all_users"),
]

router = DefaultRouter()
router.register(r"api/roles", RoleViewSet, basename="role")
router.register(r"api/permissions", PermissionViewSet, basename="permission")
router.register(r"api/resources", ResourceViewSet, basename="resource")
router.register(r"api/userroles", UserRoleViewSet, basename="userrole")
router.register(
    r"api/rolepermissions", RolePermissionViewSet, basename="rolepermission"
)

urlpatterns += router.urls
