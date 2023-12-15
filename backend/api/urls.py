from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientViewSet, NeoViewSet, RecipeViewSet, ShoppingCartViewSet, TagViewSet)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)
router.register(r'users', CustomUserViewSet, basename='users')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    #path('users/me/', CustomUserViewSet),
    #path('', include('djoser.urls')),
    path('', include(router.urls)),
]
