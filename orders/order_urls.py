from django.urls import path
from .views import PlaceOrderView, OrderListView, OrderDetailView, UpdateOrderStatusView, PaymentDetailView, InitiateEsewaPaymentView, VerifyEsewaPaymentView

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('place/', PlaceOrderView.as_view(), name='order-place'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/status/', UpdateOrderStatusView.as_view(), name='order-status'),
    path('<int:order_id>/payment/', PaymentDetailView.as_view(), name='order-payment'),
    path('<int:order_id>/esewa/initiate/', InitiateEsewaPaymentView.as_view(), name='esewa-initiate'),
    path('esewa/verify/', VerifyEsewaPaymentView.as_view(), name='esewa-verify'),


]