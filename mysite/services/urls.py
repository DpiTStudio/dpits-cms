from django.urls import path
from . import views, cart_views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='list'),
    path('category/<slug:slug>/', views.service_category, name='category'),
    path('<slug:slug>/', views.service_detail, name='detail'),
    path('cart/add/<int:service_id>/', cart_views.cart_add, name='cart_add'),
    path('cart/remove/<int:service_id>/', cart_views.cart_remove, name='cart_remove'),
    path('cart/clear/', cart_views.cart_clear, name='cart_clear'),

]
