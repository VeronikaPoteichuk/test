from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from .models import Role, Permission, Resource, UserRole, RolePermission
from .rbac_serializers import (
    RoleSerializer,
    PermissionSerializer,
    ResourceSerializer,
    UserRoleSerializer,
    RolePermissionSerializer,
)


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        return UserRole.objects.filter(user=user, role__name="admin").exists()


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdminRole]


class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminRole]


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = [IsAdminRole]


class UserRoleViewSet(viewsets.ModelViewSet):
    @action(
        detail=False,
        methods=["post"],
        url_path="assign",
        permission_classes=[IsAdminRole],
    )
    def assign_role(self, request):
        user_id = request.data.get("user_id")
        role_id = request.data.get("role_id")
        if not user_id or not role_id:
            return Response({"error": "user_id и role_id обязательны"}, status=400)
        from django.contrib.auth.models import User

        try:
            user = User.objects.get(id=user_id)
            role = Role.objects.get(id=role_id)
        except (User.DoesNotExist, Role.DoesNotExist):
            return Response({"error": "Пользователь или Роль не найдены"}, status=404)
        UserRole.objects.get_or_create(user=user, role=role)
        return Response(
            {"success": f"Роль {role.name} назначена пользователю {user.username}"}
        )

    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAdminRole]


class RolePermissionViewSet(viewsets.ModelViewSet):
    @action(
        detail=False,
        methods=["post"],
        url_path="assign",
        permission_classes=[IsAdminRole],
    )
    def assign_permission(self, request):
        role_id = request.data.get("role_id")
        permission_id = request.data.get("permission_id")
        resource_id = request.data.get("resource_id")
        if not role_id or not permission_id or not resource_id:
            return Response(
                {"error": "role_id, permission_id, resource_id обязательны"}, status=400
            )
        try:
            role = Role.objects.get(id=role_id)
            permission = Permission.objects.get(id=permission_id)
            resource = Resource.objects.get(id=resource_id)
        except (Role.DoesNotExist, Permission.DoesNotExist, Resource.DoesNotExist):
            return Response(
                {"error": "Роль, Разрешение или Ресурс не найдены"}, status=404
            )
        RolePermission.objects.get_or_create(
            role=role, permission=permission, resource=resource
        )
        return Response(
            {
                "success": f"Разрешение {permission.code} для ресурса {resource.name} назначено роли {role.name}"
            }
        )

    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAdminRole]
