import re

from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from users.models import Follow

from .fields import Base64ImageField, Hex2NameColor
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password',
                  'first_name', 'last_name')

    def validate_username(self, username):
        if not re.match(r'^[\w.@+-]+$', username):
            raise serializers.ValidationError('Недопустимые символы')
        if username.lower() == 'me':
            raise serializers.ValidationError('Недопустимое имя')
        return username


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Follow.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients',
        read_only=True,
    )
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time', 'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return Favorite.objects.filter(
                user=request.user, recipe=obj,
            ).exists()
        return False

    def get_is_in_shopping_cart(self, instance):
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return instance.shopping_cart.filter(user=request.user).exists()
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True, required=False)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True,
    )
    is_favorited = serializers.BooleanField(read_only=True, default=False)
    is_in_shopping_cart = serializers.BooleanField(read_only=True,
                                                   default=False)

    def ingredients_data_create(self, ingredients_data, recipe):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                ingredient=ingredient.get('ingredient'),
                recipe=recipe,
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients_data
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.ingredients_data_create(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.ingredients_data_create(ingredients_data, instance)
        return super().update(instance, validated_data)

    def validate(self, data):
        ingredients = self.context.get('request').data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'errors': 'Добавьте ингредиенты'},
                status.HTTP_400_BAD_REQUEST,
            )
        tags = self.context.get('request').data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'errors': 'Добавьте теги'},
                status.HTTP_400_BAD_REQUEST,
            )
        return data

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'errors': 'Добавьте ингредиенты'},
                status.HTTP_400_BAD_REQUEST,
            )
        ingredients = []
        for ingredient in data:
            if ingredient['ingredient'].id in ingredients:
                raise serializers.ValidationError(
                    {'errors': 'Ингредиенты должны быть уникальными'},
                    status.HTTP_400_BAD_REQUEST,
                )
            ingredients.append(ingredient['ingredient'].id)
        return data

    def validate_tags(self, data):
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'errors': 'Добавьте теги'},
                status.HTTP_400_BAD_REQUEST,
            )
        tags = []
        for tag in data:
            if tag in tags:
                raise serializers.ValidationError(
                    {'errors': 'Теги должны быть уникальными'},
                    status.HTTP_400_BAD_REQUEST,
                )
            tags.append(tag)
        return data

    def validate_cooking_time(self, data):
        if data <= 0:
            raise serializers.ValidationError(
                {'errors': 'Время приготовления должно быть больше нуля'},
                status.HTTP_400_BAD_REQUEST,
            )
        return data

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={'request': self.context.get('request')},
        ).data

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time', 'is_favorited',
            'is_in_shopping_cart',
        )


class FollowCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        if self.context['request'].method == 'POST':
            if self.context['request'].user == data['author']:
                raise serializers.ValidationError(
                    'Нельзя подписаться на самого себя',
                )
            if Follow.objects.filter(
                user=self.context['request'].user,
                author=data['author']
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого пользователя',
                )
        if self.context['request'].method == 'DELETE':
            if not Follow.objects.filter(
                user=self.context['request'].user,
                author=data['author']
            ).exists():
                raise serializers.ValidationError(
                    'Вы не подписаны на этого пользователя',
                )

        return data


class FollowSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes(self, obj):
        recipes_queryset = Recipe.objects.filter(author=obj)
        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            if 'recipes_limit' in request.GET:
                recipes_limit = request.GET.get('recipes_limit')
                if recipes_limit:
                    recipes_queryset = recipes_queryset[:int(recipes_limit)]

        return RecipeShortSerializer(
            recipes_queryset,
            context={'request': request},
            many=True,
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
