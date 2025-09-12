from django.shortcuts import render, redirect
from .models import Profile
from django.contrib.auth.models import User
from .models import Profile
from django import forms
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .access_utils import check_access


class RegisterForm(forms.ModelForm):
	first_name = forms.CharField(max_length=30, required=True, label="Имя")
	last_name = forms.CharField(max_length=30, required=True, label="Фамилия")
	patronymic = forms.CharField(max_length=30, required=True, label="Отчество")
	email = forms.EmailField(required=True, label="Email")
	password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
	password2 = forms.CharField(widget=forms.PasswordInput, label="Повтор пароля")

	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email', 'password')

	def clean(self):
		cleaned_data = super().clean()
		password = cleaned_data.get("password")
		password2 = cleaned_data.get("password2")
		if password and password2 and password != password2:
			self.add_error('password2', "Пароли не совпадают")
		return cleaned_data

def register(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			user_qs = User.objects.filter(email=email)
			from authtest.models import Role, UserRole
			user_role, _ = Role.objects.get_or_create(name='user')
			if user_qs.exists():
				user = user_qs.first()
				if not user.is_active:
					user.username = email
					user.first_name = form.cleaned_data['first_name']
					user.last_name = form.cleaned_data['last_name']
					user.set_password(form.cleaned_data['password'])
					user.is_active = True
					user.save()
					profile, _ = Profile.objects.get_or_create(user=user)
					profile.patronymic = form.cleaned_data['patronymic']
					profile.save()
					UserRole.objects.get_or_create(user=user, role=user_role)
					return redirect('login')
				else:
					form.add_error('email', 'Пользователь с таким email уже существует и активен.')
			else:
				user = User.objects.create_user(
					username=email,
					email=email,
					password=form.cleaned_data['password'],
					first_name=form.cleaned_data['first_name'],
					last_name=form.cleaned_data['last_name'],
				)
				Profile.objects.create(
					user=user,
					patronymic=form.cleaned_data['patronymic']
				)
				UserRole.objects.get_or_create(user=user, role=user_role)
				return redirect('login')
	else:
		form = RegisterForm()
	return render(request, 'register.html', {'form': form})

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="Имя")
    last_name = forms.CharField(max_length=30, required=True, label="Фамилия")
    patronymic = forms.CharField(max_length=30, required=True, label="Отчество")
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = Profile
        fields = ('patronymic',)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['patronymic'].initial = getattr(user.profile, 'patronymic', '')


@login_required
def profile_view(request):
	user = request.user
	view_access, view_code = check_access(user, 'profile', 'view_profile')
	if view_code == 401:
		return HttpResponse('Unauthorized', status=401)
	if view_code == 403:
		return HttpResponse('Forbidden', status=403)
	profile, created = Profile.objects.get_or_create(user=user)
	can_edit, edit_code = check_access(user, 'profile', 'edit_profile')
	if request.method == 'POST':
		if not can_edit:
			return HttpResponse('Forbidden', status=403)
		if 'delete_account' in request.POST:
			user.is_active = False
			user.save()
			from django.contrib.auth import logout
			logout(request)
			return redirect('home')
		form = ProfileForm(request.POST, instance=profile, user=user)
		if form.is_valid():
			user.first_name = form.cleaned_data['first_name']
			user.last_name = form.cleaned_data['last_name']
			user.email = form.cleaned_data['email']
			user.save()
			profile.patronymic = form.cleaned_data['patronymic']
			profile.save()
			return redirect('profile')
	else:
		form = ProfileForm(instance=profile, user=user)
	return render(request, 'profile.html', {
		'form': form,
		'can_edit': can_edit,
		'user': user,
		'profile_obj': profile,
	})

def base_context(request):
	profile = None
	if request.user.is_authenticated:
		try:
			profile = Profile.objects.get(user=request.user)
			from .models import UserRole, Role
			admin_role = Role.objects.filter(name='admin').first()
			if admin_role:
				has_admin = UserRole.objects.filter(user=request.user, role=admin_role).exists()
				if has_admin and profile.role != admin_role:
					profile.role = admin_role
					profile.save()
		except Profile.DoesNotExist:
			profile = None
	return {'profile_obj': profile}

@login_required
def all_users_view(request):
	if not request.user.is_authenticated:
		return JsonResponse({'error': 'Unauthorized'}, status=401)
	User = get_user_model()
	users = User.objects.all()
	users_data = [
		{
			'id': user.id,
			'username': user.username,
			'email': user.email,
			'first_name': user.first_name,
			'last_name': user.last_name,
		}
		for user in users
	]
	return JsonResponse({'users': users_data})

from .access_utils import check_access

@login_required
def assign_role_page(request):
	user = request.user
	can_assign, code = check_access(user, 'userrole', 'assign_role')
	if not can_assign:
		return HttpResponse('Forbidden', status=403)
	return render(request, 'assign_role.html', {'can_assign_role': True})
