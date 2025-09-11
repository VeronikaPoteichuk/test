from django.urls import path, include
from .views import register, profile_view
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='base.html'), name='home'),
    path('register/', register, name='register'),
    path('profile/', profile_view, name='profile'),
    path('accounts/', include('django.contrib.auth.urls')),
]
