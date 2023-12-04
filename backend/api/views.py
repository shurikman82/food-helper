from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, serializers, status, viewsets
from .serializers import (
    CustomUserSerializer,
    FollowSerializer, FollowCreateSerializer, NeoSerializer, ShoppingCartSerializer,
    CustomUserCreateSerializer, IngredientSerializer, RecipeCreateSerializer, RecipeShortSerializer,
    RecipeSerializer, TagSerializer,
)

from recipes.models import Recipe, Tag, Ingredient, Neo, RecipeIngredient
from users.models import Follow



User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class CustomUserCreateViewSet(UserViewSet):
    serializer_class = CustomUserCreateSerializer
    queryset = User.objects.all()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким никнеймом уже существует')
        return value


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FollowCreateSerializer
        return FollowSerializer
    
    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)
    

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH', 'DELETE'):
            return RecipeCreateSerializer
        return RecipeSerializer
