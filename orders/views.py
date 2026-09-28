from django.shortcuts import render

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import (
    CartSerializer, 
    CartItemSerializer, 
    AddCartItemSerializer, 
    UpdateCartItemSerializer
) 

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