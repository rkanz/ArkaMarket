from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from shop import views as shop_views


urlpatterns = [
    path('admin/',admin.site.urls),

    path('',shop_views.index,name='index'),
    path('about/',shop_views.about,name='about'),
    path('contact/',shop_views.contact_view,name='contact'),
    path('search/',shop_views.search,name='search'),
    path('shop/',include('shop.urls',namespace='shop')),
    path('accounts/',include('accounts.urls')),
    path('cart/',include('cart.urls',namespace='cart')),
    path('api/',include('api.urls')),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
