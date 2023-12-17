from io import BytesIO
import os
from django.contrib.auth import get_user_model
from django.db.models.aggregates import Sum
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import UserCreateSerializer
from djoser.views import UserViewSet
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .serializers import (
    CustomUserSerializer,
    FollowSerializer, NeoSerializer, ShoppingCartSerializer,
    CustomUserCreateSerializer, IngredientSerializer, RecipeIngredientCreateSerializer, RecipeCreateSerializer,
    RecipeSerializer, RecipeShortSerializer, TagSerializer,
)
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPagination
from .permissions import ForRecipePermission, IsOnlyAuthor
from recipes.models import Recipe, Tag, Ingredient, Neo, RecipeIngredient, ShoppingCart
from users.models import Follow


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['username']

#    def get_queryset(self):
#        limit = self.request.query_params.get('limit')
#       if limit:
#            return User.objects.all()[:int(limit)]
#       return User.objects.all()

#    def get_serializer_class(self):
#        if self.request.method in SAFE_METHODS:
#            return CustomUserSerializer
#        return CustomUserCreateSerializer
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким никнеймом уже существует')
        return value
    
    @action(
        methods=['delete', 'post'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        user = self.request.user
        author = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            if user == author:
                return Response({'errors': 'Нельзя подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(user=user, author=author).exists():
                return Response({'errors': 'Вы уже подписаны на этого пользователя'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not Follow.objects.filter(user=user, author=author).exists():
                return Response({'errors': 'Вы не подписаны на этого пользователя'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
        serializer_class=FollowSerializer,
    )
    def subscriptions(self, request):
        user = self.request.user
        subscriptions_queryset = Follow.objects.filter(user=user)
        authors = [item.author.id for item in subscriptions_queryset]
        users_queryset = User.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(users_queryset)
        serializer = FollowSerializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)
        
        
    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
        pagination_class=None,
        url_path='me',
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)
    
   #class CustomUserCreateViewSet(UserViewSet):
#    serializer_class = CustomUserCreateSerializer
 #   queryset = User.objects.all()

 #   def validate_username(self, value):
 #       if User.objects.filter(username=value).exists():
 #           raise serializers.ValidationError('Пользователь с таким никнеймом уже существует')
  #      return value


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    permission_classes = [IsAuthenticated,]
    serializer_class = FollowSerializer

    
    
    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)
    

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = [ForRecipePermission]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        user = request.user
        
        if not Recipe.objects.filter(id=pk).exists():
            return Response({'errors': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = Recipe.objects.get(id=pk)
        if user.neo.filter(recipe=recipe).exists():
            return Response({'errors': 'Рецепт уже в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            Neo.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            user.neo.filter(recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        user = self.request.user
        
        if not Recipe.objects.filter(id=pk).exists():
            return Response({'errors': 'Рецепт не найден'},
                            status=status.HTTP_400_BAD_REQUEST)
        recipe = Recipe.objects.get(id=pk)
        if user.shopping_cart.filter(recipe=recipe).exists():
            return Response({'errors': 'Рецепт уже в списке покупок'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            try:
                user.shopping_cart.get(recipe=recipe).delete()
            except ShoppingCart.DoesNotExist:
                return Response({'errors': 'Рецепта нет в списке покупок'},
                                status=status.HTTP_404_NOT_FOUND)
            user.shopping_cart.filter(recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated],
        pagination_class=None,
    )
    def download_shopping_cart(self, request):
        pdfmetrics.registerFont(TTFont('ArialRegular', 'ArialRegular.ttf'))
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        pdf.setFont('ArialRegular', 16)
        ingredients_list = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
            ).values(
                'ingredient__name', 'ingredient__measurement_unit',
            ).annotate(amount=Sum('amount'))
        if ingredients_list:
            pdf.drawString(200, 800, text='Что купить:')
            y_position = 780
            for index, ingredient in enumerate(ingredients_list, start=1):
                text = (f'{index}. {ingredient["ingredient__name"]}'
                        f' {ingredient["amount"]}'
                        f'{ingredient["ingredient__measurement_unit"]}.')
                pdf.drawString(100, y_position, text)
                y_position -= 20
            pdf.save()
            buffer.seek(0)
            response = FileResponse(
                buffer, as_attachment=True, filename='shopping_cart.pdf',
            )
            return response

        pdf.drawString(200, 800, text='Список покупок пуст!')
        pdf.save()
        buffer.seek(0)
        response = FileResponse(
            buffer, as_attachment=False, filename='shopping_cart.pdf')
        return response
        
        



class NeoViewSet(viewsets.ModelViewSet):
    queryset = Neo.objects.all()
    serializer_class = NeoSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ShoppingCartSerializer


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientCreateSerializer
