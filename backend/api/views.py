from io import BytesIO

from django.contrib.auth import get_user_model
from django.db.models.aggregates import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .mixins import FavoriteAndShoppingCartActionsMixin
from .pagination import CustomPagination
from .permissions import ForRecipePermission
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from .serializers import (FavoriteSerializer, FollowCreateSerializer,
                          FollowSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeIngredientCreateSerializer, RecipeSerializer,
                          ShoppingCartSerializer,
                          TagSerializer)
from users.models import Follow

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['username']

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id=None):
        if request.method == 'POST':
            return self.subscribe_action(request, id)
        return self.unsubscribe_action(request, id)

    def subscribe_action(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, pk=id)
        serializer = FollowCreateSerializer(
            context={'request': request},
            data={'author': author.id, 'user': user.id},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = FollowSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def unsubscribe_action(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, pk=id)
        subscription = Follow.objects.filter(author=author.id, user=user.id)
        if not subscription:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
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
        authors = subscriptions_queryset.values_list('author_id', flat=True)
        users_queryset = User.objects.filter(pk__in=authors)
        paginated_queryset = self.paginate_queryset(users_queryset)
        serializer = FollowSerializer(
            paginated_queryset, many=True, context={'request': request},
        )
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


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    permission_classes = [IsAuthenticated]
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


class RecipeViewSet(viewsets.ModelViewSet,
                    FavoriteAndShoppingCartActionsMixin):
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
    def favorite(self, request, pk, model=Favorite):
        return self.favorite_and_shopping_cart_actions(
            request, pk, model
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk, model=ShoppingCart):
        return self.favorite_and_shopping_cart_actions(
            request, pk, model
        )

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
        ).annotate(ingredient_amount=Sum('amount'))
        if ingredients_list:
            pdf.drawString(200, 800, text='Что купить:')
            y_position = 780
            for index, ingredient in enumerate(ingredients_list, start=1):
                text = (f'{index}. {ingredient["ingredient__name"]}'
                        f' {ingredient["ingredient_amount"]}'
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


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ShoppingCartSerializer


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientCreateSerializer
