from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from .serializers import (
    CustomUserSerializer,
    FollowSerializer, FollowCreateSerializer, NeoSerializer, ShoppingCartSerializer,
    CustomUserCreateSerializer, IngredientSerializer, RecipeIngredientCreateSerializer, RecipeCreateSerializer,
    RecipeSerializer, TagSerializer,
)

from recipes.models import Recipe, Tag, Ingredient, Neo, RecipeIngredient, ShoppingCart
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
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Neo, request.user, pk)
        return self.remove_from(Neo, request.user, pk)

    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(ShoppingCart, request.user, pk)
        return self.remove_from(ShoppingCart, request.user, pk)


class NeoViewSet(viewsets.ModelViewSet):
    queryset = Neo.objects.all()
    serializer_class = NeoSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ShoppingCartSerializer


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientCreateSerializer
