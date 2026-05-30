from django.shortcuts import render,redirect,get_object_or_404
from shop.models import Product
from . models import Cart,CartItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
# Create your views here.


def add_to_cart(request,slug):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    product = Product.objects.get(slug=slug)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    quantity=int(request.POST.get('quantity',1))

    try:
        if quantity > product.stock_quantity:
            raise ValueError("موجودی کافی نیست!!")
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            if (cart_item.quantity + quantity) > product.stock_quantity:
                raise ValueError("موجودی کافی نیست !!")
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
    except ValueError as e:
        messages.error(request,str(e))
    messages.success(request,f"محصول {product.name}   به سبد خرید اضافه شد .")
    return redirect('cart:cart_detail')



def cart_detail(request):
    if not request.user.is_authenticated:
        return render(request,'cart/cart_detail.html',{
            'cart':None,
            'items':[],
            'total_price':0
        })
    cart=Cart.objects.filter(user=request.user).first()

    if not cart:
        return render(request,'cart/cart_detail.html',{
            'cart':None,
            'items':[],
            'total_price':0
        })
    items=cart.items.all()
    total_price=0
    for item in items:
        total_price+=item.total_price
    return render(request,'cart/cart_detail.html',{
        'cart':cart,
        'items':items,
        'total_price':total_price
    })

def update_cart(request,item_id):
    cart_item=get_object_or_404(CartItem,id=item_id,cart__user=request.user)
    action=request.POST.get('action')
    product=cart_item.product

    if action == 'remove':
        cart_item.delete()
    elif action == 'update':
        quantity=int(request.POST.get('quantity',1))
        if quantity>product.stock_quantity:
            messages.warning(request,f"متاسفانه فقط { product.stock_quantity} عدد از این محصول موجود است .")
            cart_item.quantity=product.stock_quantity
        elif quantity<=0:
            cart_item.delete()
        else:
            cart_item.quantity=quantity
        cart_item.save()
    return redirect('cart:cart_detail')
