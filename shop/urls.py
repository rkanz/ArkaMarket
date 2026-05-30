from django.urls import path
from . import views


app_name='shop'

urlpatterns=[
    path('',views.shop,name='shop_home'),#www.arkamarket.com/shop/
    # path('brand/<int:brand_id>/', views.brand_products, name='brand_products'),# www.arkamarket.com/shop/brand/brand_id/
    path('category/<slug:category_slug>/', views.shop, name='shop_by_category'),#www.arkamarket.com/shop/category/slug/
    path('<slug:slug>/',views.shop_single,name='shop_single'),#www.arkamarket.com/shop/slug/
    path('<slug:slug>/rate/',views.rate_product,name='rate_product'),#www.arkamarket.com/shop/slug/rate/
]