from authtest.models import RolePermission, UserRole, Resource, Permission

def check_access(user, resource_name, permission_code):
    if not user.is_authenticated:
        return None, 401
    if user.is_superuser:
        return True, 200
    user_roles = UserRole.objects.filter(user=user).values_list('role', flat=True)
    resource = Resource.objects.filter(name=resource_name).first()
    permission = Permission.objects.filter(code=permission_code).first()
    if not resource or not permission:
        return None, 403
    allowed = RolePermission.objects.filter(role__in=user_roles, resource=resource, permission=permission).exists()
    if allowed:
        return True, 200
    return None, 403