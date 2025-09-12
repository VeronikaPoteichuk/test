from rest_framework import permissions, viewsets
from django.contrib.auth.models import User
from .models import Profile
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['patronymic']


class ProfileFullSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Profile
        fields = ['user', 'patronymic']

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class ProfileMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'patronymic': profile.patronymic,
            'is_active': user.is_active,
        }
        return Response(data)

    def put(self, request):
        user = request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        profile.patronymic = request.data.get('patronymic', profile.patronymic)
        user.save()
        profile.save()
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'patronymic': profile.patronymic,
            'is_active': user.is_active,
        }
        return Response(data)
