from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegisterForm,ProfileUpdateForm
from django.contrib import messages
from django.contrib.auth import authenticate,login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Profile
from shop.models import Product
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .tasks import send_welcome_email
# Create your views here.
class RegisterView(CreateView):
    form_class=RegisterForm
    template_name="registration/register.html"
    success_url=reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)

        send_welcome_email.delay(self.object.pk)

        return response

def login_view(request):
    if request.method == "POST":
        username=request.POST.get("username")
        password=request.POST.get("password")

        user =authenticate(request,username=username,password=password)
        if user is not None:
            auth_login(request,user)
            messages.success(request,"با موفقیت وارد سایت شدید.")
            return redirect("index")
        else:
            messages.error(request,"نام کاربری یا رمز عبور اشتباه وارد شده است.")
    return render(request,"registration/login.html")
#برای خروج کاربر
def logout_view(request):
    logout(request)
    messages.info(request,"با موفقیت  خارج شدید.")
    return redirect('accounts:login')


@login_required
def profile_edit(request):
    profile,_=Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form=ProfileUpdateForm(request.POST,instance=profile,user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request,"اطلاعات پروفایل با موفقیت برروزرسانی شد.")
            return redirect("accounts:profile")
        else:
            messages.error(request,"لطفا خطا های فرم را بررسی نمایید.")

    else:
        form=ProfileUpdateForm(instance=profile,user=request.user)
    return render(request,"registration/profile_edit.html",{"form":form})

def profile_view(request):
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        return render(request, "registration/profile.html", {"profile": profile})
    else:
        return redirect("accounts:login")


@require_POST
@login_required
def add_to_favorites(request, slug):
    if request.method != "POST":
        return JsonResponse({
            'success': False,
            'message': 'Invalid request method'
        }, status=405)

    product = get_object_or_404(Product, slug=slug)
    profile=get_object_or_404(Profile,user=request.user)


    if product in profile.favorites_products.all():
        profile.favorites_products.remove(product)
        is_favorite = False
    else:
        profile.favorites_products.add(product)
        is_favorite = True

    return JsonResponse({
        'success': True,
        'is_favorite': is_favorite
    })
@login_required
def toggle_favorite(request,slug):
    if request.method !='POST':
        return redirect('shop_single',slug=slug)

    product=get_object_or_404(Product,slug=slug)
    profile=request.user.profile

    if product in profile.favorites_products.all():
        profile.favorites_products.remove(product)
        messages.success(request,"محصول از علاقه مندی ها حذف شد .")
    else:
        profile.favorites_products.add(product)
        messages.success(request,"محصول به علاقه مندی ها اضافه شد.")
    return redirect('accounts:my_favorites')


@login_required
def my_favorites(request):
    user_profile=request.user.profile
    favorite_products=user_profile.favorites_products.all()

    context={
        'products':favorite_products,
        'title':'محصولات مورد علاقه من'
    }
    return render(request,'registration/my_favorites.html',context)

