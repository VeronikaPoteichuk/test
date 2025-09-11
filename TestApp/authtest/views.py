from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile
from django import forms
from django.contrib.auth.decorators import login_required


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
			user = User.objects.create_user(
				username=form.cleaned_data['email'],
				email=form.cleaned_data['email'],
				password=form.cleaned_data['password'],
				first_name=form.cleaned_data['first_name'],
				last_name=form.cleaned_data['last_name'],
			)
			Profile.objects.create(
				user=user,
				patronymic=form.cleaned_data['patronymic']
			)
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
    profile, created = Profile.objects.get_or_create(user=user)
    if request.method == 'POST':
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
    return render(request, 'profile.html', {'form': form})
