from django.shortcuts import render

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db import transaction
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Order, OrderItem
from .serializers import OrderSerializer, PlaceOrderSerializer,OrderItemSerializer

from .models import Cart, CartItem, Payment
from .serializers import (
    CartSerializer, 
    CartItemSerializer, 
    AddCartItemSerializer, 
    UpdateCartItemSerializer
) 


from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers
from restaurant.permissions import IsStaffOrOwner
from .models import Order, OrderItem

# Create your views here.
def get_user_cart(user):
    cart,_ = Cart.objects.get_or_create(user=user)
    return cart

class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=CartSerializer)
    def get(self, request):
        cart = get_user_cart(request.user)
        return Response(CartSerializer(cart).data)

    @extend_schema(request=None, responses={204: None})
    def delete(self, request):
        cart = get_user_cart(request.user)
        cart.items.all().delete()
        return Response(status=204)

class CartItemAddView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=AddCartItemSerializer, responses=CartSerializer)
    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        menu_item = serializer.validated_data['menu_item']
        quantity = serializer.validated_data['quantity']

        cart = get_user_cart(request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart, menu_item=menu_item, defaults={'quantity': quantity}
        )

        if not created:
            item.quantity += quantity
            item.save()
        return Response(CartSerializer(cart).data, status=201)


class CartItemDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=UpdateCartItemSerializer, responses=CartSerializer)
    def patch(self,request,pk):
        cart = get_user_cart(request.user)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item.quantity = serializer.validated_data['quantity']
        item.save()
        return Response(CartSerializer(cart).data)


    @extend_schema(responses={204:None})    
    def delete(self, request, pk):
        cart = get_user_cart(request.user)
        item = get_object_or_404(CartItem, pk=pk, cart=cart)
        return Response(status=204)



class PlaceOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=PlaceOrderSerializer, responses=OrderSerializer)
    def post(self, request):
        serializer = PlaceOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_user_cart(request.user)
        cart_items = list(cart.items.all())

        if not cart_items:
            return Response({'detail': 'Your cart is empty.'}, status=400)

        with transaction.atomic():
            total = sum(item.menu_item.price * item.quantity for item in cart_items)
            order = Order.objects.create(
                user=request.user,
                total_amount=total,
                delivery_address=serializer.validated_data['delivery_address'],
            )
            Payment.objects.create(order=order, method='cod')
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=item.menu_item,
                    quantity=item.quantity,
                    price_at_order=item.menu_item.price,
                )
            cart_items_qs = cart.items.all()
            cart_items_qs.delete()

        return Response(OrderSerializer(order).data, status=201)

class OrderListView(ListAPIView):
    serializer_class=OrderSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(RetrieveAPIView):
    serializer_class=OrderSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


VALID_TRANSITIONS = {
    'pending': ['confirmed', 'cancelled'],
    'confirmed': ['preparing', 'cancelled'],
    'preparing': ['out_for_delivery'],
    'out_for_delivery': ['delivered'],
    'delivered': [],
    'cancelled': [],
}

class UpdateOrderStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsStaffOrOwner]

    @extend_schema(
        request=inline_serializer(
            name='UpdateOrderStatus',
            fields={'status': drf_serializers.ChoiceField(choices=Order.STATUS_CHOICES)},
        ),
        responses=OrderSerializer,
    )
    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.data.get('status')

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'detail': 'Invalid status value.'}, status=400)

        allowed_next = VALID_TRANSITIONS.get(order.status, [])
        if new_status not in allowed_next:
            return Response(
                {'detail': f'Cannot move from {order.status} to {new_status}.'},
                status=400,
            )

        order.status = new_status
        order.save()
        return Response(OrderSerializer(order).data)

from .serializers import PaymentSerializer


class PaymentDetailView(RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'order_id'

    def get_queryset(self):
        user = self.request.user
        if user.role in ['staff', 'owner']:
            return Payment.objects.all()
        return Payment.objects.filter(order__user=user)

import hashlib
import hmac
import base64
import uuid
from django.conf import settings


class InitiateEsewaPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, user=request.user)
        payment = order.payment

        if payment.status == 'completed':
            return Response({'detail': 'This order is already paid.'}, status=400)

        transaction_uuid = str(uuid.uuid4())
        amount = str(order.total_amount)

        message = f"total_amount={amount},transaction_uuid={transaction_uuid},product_code={settings.ESEWA_MERCHANT_CODE}"
        signature = base64.b64encode(
            hmac.new(
                settings.ESEWA_SECRET_KEY.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256,
            ).digest()
        ).decode('utf-8')

        payment.method = 'esewa'
        payment.transaction_uuid = transaction_uuid
        payment.save()

        return Response({
            'payment_url': settings.ESEWA_PAYMENT_URL,
            'form_data': {
                'amount': amount,
                'tax_amount': '0',
                'total_amount': amount,
                'transaction_uuid': transaction_uuid,
                'product_code': settings.ESEWA_MERCHANT_CODE,
                'product_service_charge': '0',
                'product_delivery_charge': '0',
                'success_url': 'http://127.0.0.1:8000/api/orders/esewa/verify/',
                'failure_url': 'http://127.0.0.1:8000/api/orders/esewa/verify/',
                'signed_field_names': 'total_amount,transaction_uuid,product_code',
                'signature': signature,
            },
        })

import requests
import json

class VerifyEsewaPaymentView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        encoded_data = request.query_params.get('data')
        if not encoded_data:
            return Response({'detail': 'Missing payment data.'}, status=400)

        decoded = base64.b64decode(encoded_data).decode('utf-8')
        data = json.loads(decoded)

        transaction_uuid = data.get('transaction_uuid')
        status_from_esewa = data.get('status')

        payment = get_object_or_404(Payment, transaction_uuid=transaction_uuid)

        if status_from_esewa != 'COMPLETE':
            payment.status = 'failed'
            payment.save()
            return Response({'detail': 'Payment was not completed.'}, status=400)

        verify_response = requests.get(
            settings.ESEWA_VERIFY_URL,
            params={
                'product_code': settings.ESEWA_MERCHANT_CODE,
                'total_amount': data.get('total_amount'),
                'transaction_uuid': transaction_uuid,
            },
        )
        result = verify_response.json()

        if result.get('status') == 'COMPLETE':
            payment.status = 'completed'
            payment.transaction_id = data.get('transaction_code', '')
            payment.save()
            return Response({'detail': 'Payment verified and completed.'})
        else:
            payment.status = 'failed'
            payment.save()
            return Response({'detail': 'Verification failed.'}, status=400)