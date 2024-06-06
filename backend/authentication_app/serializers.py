from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import UserAccount

# Get the User model dynamically
User = get_user_model()

class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'name', 'password',  'registered_date', 'subscription_status', 'subscription_date')

