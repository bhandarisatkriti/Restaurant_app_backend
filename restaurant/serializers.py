from rest_framework import serializers
from .models import Restaurant

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields=['id','name','address','logo','phone','opening_time','closing_time','is_active']