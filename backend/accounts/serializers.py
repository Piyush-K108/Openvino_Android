from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from accounts.models import *
from rest_framework import serializers
user = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = user
        fields = "__all__"

class Phone(serializers.ModelSerializer):
    class Meta:
        model = UserAccounts
        fields = ('phone')



class UserAccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccounts
        fields = ['ProfilePic']


