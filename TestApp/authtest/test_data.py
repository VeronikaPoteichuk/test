from .models import Role, Resource, Permission, RolePermission, UserRole
from django.contrib.auth.models import User

def create_test_rbac_data():
	# Роли
	admin_role, _ = Role.objects.get_or_create(name='admin', description='Администратор')
	user_role, _ = Role.objects.get_or_create(name='user', description='Пользователь')
	guest_role, _ = Role.objects.get_or_create(name='guest', description='Гость')
	# Ресурсы
	profile_res, _ = Resource.objects.get_or_create(name='profile', description='Профиль пользователя')
	assign_role_res, _ = Resource.objects.get_or_create(name='assign_role', description='Назначение ролей')
	# Разрешения
	view_profile_perm, _ = Permission.objects.get_or_create(code='view_profile', description='Просмотр профиля')
	edit_profile_perm, _ = Permission.objects.get_or_create(code='edit_profile', description='Редактирование профиля')
	edit_assign_role_perm, _ = Permission.objects.get_or_create(code='assign_role_page', description='Назначение ролей')
	# Связи ролей и разрешений
	RolePermission.objects.get_or_create(role=admin_role, permission=view_profile_perm, resource=profile_res)
	RolePermission.objects.get_or_create(role=admin_role, permission=edit_profile_perm, resource=profile_res)
	RolePermission.objects.get_or_create(role=admin_role, permission=edit_assign_role_perm, resource=assign_role_res)
	RolePermission.objects.get_or_create(role=user_role, permission=view_profile_perm, resource=profile_res)
	RolePermission.objects.get_or_create(role=user_role, permission=edit_profile_perm, resource=profile_res)
	RolePermission.objects.get_or_create(role=guest_role, permission=view_profile_perm, resource=profile_res)
	# Пользователи
	admin_user, _ = User.objects.get_or_create(username='admin', email='admin@example.com', is_staff=True, is_superuser=True)
	admin_user.set_password('adminpass')
	admin_user.save()
	user_user, _ = User.objects.get_or_create(username='user', email='user@example.com')
	user_user.set_password('userpass')
	user_user.save()	
	guest_user, _ = User.objects.get_or_create(username='guest', email='guest@example.com')
	guest_user.set_password('guestpass')
	guest_user.save()
	# Назначение ролей
	UserRole.objects.get_or_create(user=admin_user, role=admin_role)
	UserRole.objects.get_or_create(user=user_user, role=user_role)
	UserRole.objects.get_or_create(user=guest_user, role=guest_role)