from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.serializers import UserCreateSerializer
from djoser.views import UserViewSet
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter

from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from .serializers import (
    CustomUserSerializer,
    FollowSerializer, FollowCreateSerializer, NeoSerializer, ShoppingCartSerializer,
    CustomUserCreateSerializer, IngredientSerializer, RecipeIngredientCreateSerializer, RecipeCreateSerializer,
    RecipeSerializer, TagSerializer,
)

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

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return CustomUserSerializer
        return CustomUserCreateSerializer
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким никнеймом уже существует')
        return value
    
    @action(
        methods=['delete', 'post'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            create = Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(create)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            Follow.objects.filter(user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

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

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FollowCreateSerializer
        return FollowSerializer
    
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
    filter_backends = [SearchFilter]
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = [ForRecipePermission]
    filter_backends = [SearchFilter]
    search_fields = ('author',)

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
        recipe = get_object_or_404(Recipe, id=pk)
        if not Recipe.objects.filter(id=pk).exists():
            return Response({'errors': 'Рецепт не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        if user.neo.filter(recipe=recipe).exists():
            return Response({'errors': 'Рецепт уже в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            created = Neo.objects.create(user=user, recipe=recipe)
            serializer = NeoSerializer(created)
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
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if not Recipe.objects.filter(id=pk).exists():
            return Response({'errors': 'Рецепт не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        if user.shopping_cart.filter(recipe=recipe).exists():
            return Response({'errors': 'Рецепт уже в списке покупок'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            created = ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = ShoppingCartSerializer(created)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            user.shopping_cart.filter(recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        



class NeoViewSet(viewsets.ModelViewSet):
    queryset = Neo.objects.all()
    serializer_class = NeoSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ShoppingCartSerializer


class RecipeIngredientViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredient.objects.all()
    serializer_class = RecipeIngredientCreateSerializer
