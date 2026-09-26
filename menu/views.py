from django.shortcuts import render
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from restaurant.permissions import IsOwnerorReadOnly
from .models import Category,MenuItem
from .serializers import CategorySerializer,MenuItemSerializer

# Create your views here.
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class=CategorySerializer
    permission_classes=[IsOwnerorReadOnly]

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset =MenuItem.objects.all()
    serializer_class=MenuItemSerializer
    permission_classes=[IsOwnerorReadOnly]
    filter_backends=[DjangoFilterBackend]
    filterset_fields=['category', 'is_available']