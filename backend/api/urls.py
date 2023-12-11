from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, NeoViewSet, RecipeViewSet, ShoppingCartViewSet, TagViewSet)

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet)
router.register(r'tags', TagViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:pk>/favorite/', RecipeViewSet.favorite({'POST': 'add', 'DELETE': 'remove'}), name='neo'),
    path('recipes/<int:pk>/shopping_cart/', RecipeViewSet.shopping_cart({'POST': 'add', 'DELETE': 'remove'}), name='shopping_cart'),
    path('', include('djoser.urls')),
    path('', include(router.urls))
]
