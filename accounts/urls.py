from django.urls import path
from .views import RegisterView, add_to_favorites
from . import views

app_name='accounts'

urlpatterns=[
    path('register/',RegisterView.as_view(),name='register'),#www.ArkaMarket.com/accounts/register/
    path('login/',views.login_view,name='login'),#www.ArkaMarket.com/accounts/login/
    path('logout/',views.logout_view,name='logout'),#www.ArkaMarket.com/accounts/logout/
    path('profile/',views.profile_view,name='profile'),#www.ArkaMarket.com/accounts/profile/
    path('add-to-favorites/<slug:slug>/',add_to_favorites,name='add_to_favorites'),#www.ArkaMarket.com/accounts/add-to-favorites/slug/
    path('favorites/',views.my_favorites,name='my_favorites'),#www.ArkaMarket.com/accoounts/favorites/
    path('toggle-favorite/<slug:slug>/',views.toggle_favorite,name='toggle_favorite'),#www.ArkaMarket.com/accounts/toggle-favorites/slug/
    path('profile/edit',views.profile_edit,name='profile_edit')#www.ArkaMarket.com/accounts/profile/edit/
]