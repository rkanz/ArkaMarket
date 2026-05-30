from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Product, Category, Rating, Banner, Brand
from django.db.models import Q,Avg,Count
from django.core.paginator import Paginator
from django.contrib import messages
from accounts.models import Profile
from .forms import ContactForm




def contact_view(request):
    if request.method =='POST':
        form=ContactForm(request.POST)
        if form.is_valid():
            contact_message=form.save()
            messages.success(request,'پیام شما با موفقیت ارسال شد.')
            return redirect ('contact')
        else:
            messages.error(request,'لطفا پیام های فرم را بررسی نمایید.')
    else:
        form=ContactForm()
    context={'form':form}
    return render(request,'shops/contact.html',context)

def index(request):
    banners=Banner.objects.filter(is_active=True).order_by('order')
    featured_products = Product.objects.filter( is_featured=True).annotate(
        average_score=Avg('ratings__score'),
        rating_count=Count('ratings')
    ).order_by('-updated_at')[:3]
    featured_categories=Category.objects.filter(
        is_featured=True
    ).order_by('name')[:3]


    return render(request, 'shops/index.html', {
        'products': featured_products,
        'featured_categories':featured_categories,
        'banners':banners

    })
def about(request):
    return render(request,'shops/about.html')

def shop_single(request,slug):
    product=get_object_or_404(Product,slug=slug)
    rating_stats=Rating.objects.filter(product=product).aggregate(
        average_score=Avg('score'),
        rating_count=Count('id')
    )
    is_favorite=False
    if request.user.is_authenticated:
        profile,created=Profile.objects.get_or_create(user=request.user)
        is_favorite=profile.favorites_products.filter(pk=product.pk).exists()



    context={
        'product':product,
        'average_score':rating_stats['average_score'],
        'rating_count': rating_stats['rating_count'],
        'is_favorite':is_favorite
    }
    return render(request,'shops/shop_single.html',context)
def search(request):
    products=Product.objects.order_by('updated_at').filter(is_available=True)
    if 'search_text' in request.GET:
        search_text = request.GET['search_text']
        if search_text:
            products=products.filter(Q(name__icontains=search_text)
                                   | Q(description__contains=search_text)
                                   | Q(brands__name__contains=search_text)
                                   | Q(category__name__contains=search_text))
    context={
                'products':products
            }
    return render(request,'shops/search.html',context)

def shop(request,category_slug=None):
    products=Product.objects.filter(is_available=True).annotate(
        average_score=Avg('ratings__score'),
        rating_count=Count('ratings')
    ).order_by('-updated_at')

    gender=request.GET.get('gender','')
    selected_brand=request.GET.get('brands','').strip()
    sort=request.GET.get('sort','')

    selected_category_obj=None


    if category_slug:
        try:
            selected_category_obj = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=selected_category_obj)
        except Category.DoesNotExist:
            return render(request,'404.html' ,status=404)



    if gender:
        products=products.filter(gender=gender)

    if selected_brand:
        products=products.filter(brands__name__iexact=selected_brand)
    if sort== 'newest':
        products=products.order_by('-created_at')
    if sort== 'oldest':
        products=products.order_by('created_at')
    elif sort== 'price_low':
        products=products.order_by('price')
    elif sort== 'price_high':
        products=products.order_by('-price')
    elif sort == 'rating':
        products=products.order_by('-average_score','-rating_count')

    all_brands=(Product.objects.exclude(brands__isnull=True).values_list('brands__name',flat=True).distinct())
    all_categories=Category.objects.all()
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    paged_products = paginator.get_page(page_number)
    context={
        'products':paged_products,
        'categories':all_categories,
        'genders':Product.GENDER_CHOICES,
        'brands':all_brands,
        'selected_category':selected_category_obj,
        'selected_brand':selected_brand,
        'selected_gender':gender,
        'selected_sort':sort,
    }
    return render(request,'shops/shop.html',context)

def all_categories(request):
    categories=Category.objects.all()
    return (request,{'categories':categories})


@login_required
def rate_product(request, slug):
    if request.method == 'POST':
        score_str = request.POST.get('score')  # دریافت امتیاز به صورت رشته
        product = get_object_or_404(Product, slug=slug)

        if score_str:  # اگر امتیازی ارسال شده باشد
            try:
                score = int(score_str)
                if not (1 <= score <= 5):  # اطمینان از اینکه امتیاز بین 1 تا 5 است
                    messages.error(request, "امتیاز باید بین 1 تا 5 باشد.")
                    return redirect(reverse('shop:shop_single', kwargs={'slug': slug}))

                user = request.user
                if user.is_authenticated:
                    # بررسی می کنیم که آیا قبلا امتیازی ثبت شده است یا خیر
                    rating, created = Rating.objects.update_or_create(
                        user=user,
                        product=product,
                        defaults={'score': score}  # مقدار امتیاز جدید
                    )

                    if created:
                        messages.success(request, "امتیاز شما با موفقیت ثبت شد.")
                    else:
                        messages.success(request, "امتیاز شما با موفقیت به روز رسانی شد.")

                else:
                    # اگر کاربر لاگین نباشد، باید به صفحه لاگین هدایت شود یا پیامی نمایش داده شود
                    messages.warning(request, "لطفاً برای ثبت امتیاز وارد حساب کاربری خود شوید.")
            except ValueError:  # اگر score_str قابل تبدیل به int نباشد
                messages.error(request, "مقدار امتیاز نامعتبر است.")
            except Exception as e:  # برای مدیریت خطاهای احتمالی دیگر
                messages.error(request, f"خطایی رخ داد: {e}")
        else:
            messages.warning(request, "امتیازی ارسال نشده است.")

        # همیشه به صفحه محصول برمی گردیم، چه امتیاز ثبت شده باشد چه نشده باشد
        return redirect(reverse('shop:shop_single', kwargs={'slug': slug}))

    else:  # اگر متد POST نباشد (مثلا GET)
        messages.error(request, "روش درخواست نامعتبر است.")
        return redirect(reverse('shop:shop_single', kwargs={'slug': slug}))

