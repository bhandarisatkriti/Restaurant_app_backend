from decimal import Decimal
from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment
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


#Order
class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'price_at_order']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_amount', 'delivery_address', 'created_at', 'items']
        read_only_fields = ['status', 'total_amount']

class PlaceOrderSerializer(serializers.Serializer):
    delivery_address = serializers.CharField()


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'method', 'status', 'transaction_id', 'paid_at']
        read_only_fields = ['method', 'status', 'transaction_id', 'paid_at']


