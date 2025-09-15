from .models import Role, Resource, Permission, RolePermission, UserRole
from django.contrib.auth.models import User

def create_test_rbac_data():
	# Роли
	admin_role, _ = Role.objects.get_or_create(name='admin', description='Администратор')
	user_role, _ = Role.objects.get_or_create(name='user', description='Пользователь')
	# Ресурсы
	profile_res, _ = Resource.objects.get_or_create(name='profile', description='Профиль пользователя')
	admin_panel_res, _ = Resource.objects.get_or_create(name='admin_panel', description='Админ-панель')
	# Разрешения
	view_profile_perm, _ = Permission.objects.get_or_create(code='view_profile', description='Просмотр профиля')
	edit_profile_perm, _ = Permission.objects.get_or_create(code='edit_profile', description='Редактирование профиля')
	view_admin_panel_perm, _ = Permission.objects.get_or_create(code='view_admin_panel', description='Просмотр админ-панели')
	# Связи ролей и разрешений
	RolePermission.objects.get_or_create(role=admin_role, permission=view_profile_perm, resource=profile_res)
	RolePermission.objects.get_or_create(role=admin_role, permission=edit_profile_perm, resource=profile_res)
	RolePermission.objects.get_or_create(role=admin_role, permission=view_admin_panel_perm, resource=admin_panel_res)
	RolePermission.objects.get_or_create(role=user_role, permission=view_profile_perm, resource=profile_res)
	# Пользователи
	admin_user, _ = User.objects.get_or_create(username='admin', email='admin@example.com')
	admin_user.set_password('adminpass')
	admin_user.save()
	user_user, _ = User.objects.get_or_create(username='user', email='user@example.com')
	user_user.set_password('userpass')
	user_user.save()
	# Назначение ролей
	UserRole.objects.get_or_create(user=admin_user, role=admin_role)
	UserRole.objects.get_or_create(user=user_user, role=user_role)