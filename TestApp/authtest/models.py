from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	patronymic = models.CharField(max_length=30, verbose_name='Отчество')

	def __str__(self):
		return f"{self.user.last_name} {self.user.first_name} {self.patronymic}"
