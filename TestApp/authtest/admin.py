from django.contrib import admin
from .models import Role, Permission, Resource, UserRole, RolePermission, Profile

class ProfileAdmin(admin.ModelAdmin):
	def get_fields(self, request, obj=None):
		fields = ['user', 'role']
		if obj:
			fields.insert(1, 'patronymic')
		return fields

admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(Resource)
admin.site.register(UserRole)
admin.site.register(RolePermission)
admin.site.register(Profile, ProfileAdmin)
