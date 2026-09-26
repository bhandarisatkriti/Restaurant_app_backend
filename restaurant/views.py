from django.shortcuts import render
from rest_framework import viewsets
from .permissions import IsOwnerorReadOnly
from .models import Restaurant
from .serializers import RestaurantSerializer

# Create your views here.
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset=Restaurant.objects.all()
    serializer_class=RestaurantSerializer
    permission_classes=[IsOwnerorReadOnly]