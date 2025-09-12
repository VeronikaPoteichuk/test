from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	patronymic = models.CharField(max_length=30, null=True, blank=True, verbose_name='Отчество')
	role = models.ForeignKey('Role', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Роль')

	def __str__(self):
		return f"{self.user.last_name} {self.user.first_name} {self.patronymic}"

	def is_admin(self):
		return self.role and self.role.name == 'admin'

class Role(models.Model):
	name = models.CharField(max_length=50, unique=True)
	description = models.TextField(blank=True)
	def __str__(self):
		return self.name

class Permission(models.Model):
	code = models.CharField(max_length=50, unique=True)
	description = models.TextField(blank=True)
	def __str__(self):
		return self.code

class Resource(models.Model):
	name = models.CharField(max_length=50, unique=True)
	description = models.TextField(blank=True)
	def __str__(self):
		return self.name

class UserRole(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	role = models.ForeignKey(Role, on_delete=models.CASCADE)
	def __str__(self):
		return f"{self.user.username} - {self.role.name}"

class RolePermission(models.Model):
	role = models.ForeignKey(Role, on_delete=models.CASCADE)
	permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
	resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
	def __str__(self):
		return f"{self.role.name} - {self.permission.code} - {self.resource.name}"
