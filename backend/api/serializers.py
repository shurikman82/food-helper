from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from users.models import Follow
from recipes.models import Ingredient, Neo, Recipe, RecipeIngredient, Tag

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):

        fields = ('email', 'username', 'password', 'first_name', 'last_name')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):

        fields = ('email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Follow.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False

    def get_count(self, obj):
        return obj.recipes.count()