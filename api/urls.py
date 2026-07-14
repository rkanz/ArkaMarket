from django.urls import path,include
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView)

urlpatterns=[
    path('products/',views.product_list_view,name='product-list'),
    path('products/<slug:slug>/',views.product_detail_view,name='product-detail'),
    path('products/<slug:slug>/ratings/',views.product_rating_view,name='product-ratings'),
    path('products/<slug:slug>/ratings/my-rating/',views.my_rating_view,name='my_rating'),
    path('products/<slug:slug>/ratings/summary/',views.ratings_summary_view,name='summary-rating'),

    path('categories/',views.category_list_view,name='category-list'),

    path('contact/',views.contact_message_view,name='contact-message'),

    path('banners/',views.banner_home_view,name='banner-home'),

    path('token/',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('token/refresh/',TokenRefreshView.as_view(),name='token_refresh'),

    path('auth/register/',views.auth_register_view,name='auth-register'),
    path('auth/profile/',views.profile_view,name='profile-view'),
    path('auth/change-password/',views.password_change_view ,name='change-password'),
    path('auth/logout/',views.logout_view,name='logout'),

    path('wishlist/',views.wishlist_view,name='wishlist'),
    path('wishlist/<int:product_id>/',views.wishlist_view,name='wishlist-detail'),
]