from django.urls import path
from . import views

app_name='cart'

urlpatterns=[
    path('add/<slug:slug>/',views.add_to_cart,name='add_to_cart'),#www.ArkaMarket.com/cart/add/slug/
    path('detail/',views.cart_detail,name='cart_detail'),#www.ArkaMarket.com/cart/detail/
    path('update/<int:item_id>/',views.update_cart,name='update_cart')#www.ArkaMarket.com/cart/update/item_id/
]