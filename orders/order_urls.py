from django.urls import path
from .views import PlaceOrderView, OrderListView, OrderDetailView, UpdateOrderStatusView

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('place/', PlaceOrderView.as_view(), name='order-place'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/status/', UpdateOrderStatusView.as_view(), name='order-status'),

]