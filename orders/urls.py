from django.urls import path
from . import views
urlpatterns = [path('', views.menu, name='menu'), path('food/<int:pk>/', views.food_detail, name='food_detail'), path('accounts/register/', views.register, name='register'), path('cart/', views.cart, name='cart'), path('cart/add/<int:pk>/', views.add_cart, name='add_cart'), path('cart/update/<int:pk>/', views.update_cart, name='update_cart'), path('checkout/', views.checkout, name='checkout'), path('orders/', views.history, name='history'), path('orders/<int:pk>/', views.order_detail, name='order_detail')]
