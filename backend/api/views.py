from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet, UserCreateViewSet
from rest_framework import permissions, status, viewsets
from .serializers import (
    CustomUserSerializer,
    FollowSerializer,
    CustomUserCreateSerializer,
)

from .models import Follow




User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer


class CustomUserCreateViewSet(UserCreateViewSet):
    serializer_class = CustomUserCreateSerializer
    queryset = User.objects.all()


class FollowViewset(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
