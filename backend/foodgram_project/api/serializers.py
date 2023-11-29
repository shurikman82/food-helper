from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from users.models import CustomUser, Follow
from recipes.models import Ingredient, Neo, Recipe, RecipeIngredient, Tag




class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = CustomUser
        fields = ('email', 'username', 'password', 'first_name', 'last_name')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = CustomUser
        fields = ('email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=self.context.get('request').user,
            author=obj,
        ).exists()

    def get_count(self, obj):
        return obj.recipes.count()