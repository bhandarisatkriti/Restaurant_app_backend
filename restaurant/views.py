from django.shortcuts import render
from rest_framework import viewsets
from .permissions import IsOwnerorReadOnly
from .models import Restaurant
from .serializers import RestaurantSerializer
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.
class RestaurantViewSet(viewsets.ModelViewSet):
    queryset=Restaurant.objects.all()
    serializer_class=RestaurantSerializer
    permission_classes=[IsOwnerorReadOnly]
    parser_classes = [MultiPartParser, FormParser]