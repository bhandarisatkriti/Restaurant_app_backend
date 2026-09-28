from decimal import Decimal
from rest_framework import serializers
from .models import Cart, CartItem
from menu.models import MenuItem

class CartItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    unit_price = serializers.DecimalField(source='menu_item.price',max_digits=8, decimal_places=2, read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'menu_item', 'menu_item_name', 'unit_price', 'subtotal', 'quantity' ]

    def get_subtotal(self,obj) -> str:
            return str(obj.menu_item.price * obj.quantity)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only = True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total']

    def get_total(self, obj) -> str:
        total = sum(
            (item.menu_item.price * item.quantity for item in obj.items.all()),
            Decimal('0.00'),
        )
        return str(total)
    
class AddCartItemSerializer(serializers.Serializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    quantity = serializers.IntegerField(min_value = 1, default =1)

    def validate_menu_item(self, value):
        if not value.is_available:
            raise serializers.ValidationError('This item is currently unavailable. ')
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value = 1 )