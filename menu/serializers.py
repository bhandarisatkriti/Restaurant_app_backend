from rest_framework import serializers
from .models import Category, MenuItem

#ModelSerializer is DRF serializer connects api serializer with django model handles its fields, validation, and basic create/update operations.

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','restaurant','name']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id','category','name','description','price','image','is_available']