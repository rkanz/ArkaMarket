from platform import processor

from django.core.validators import MinValueValidator,MaxValueValidator
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.
#مدل دسته بندی
class Category(models.Model):
    name=models.CharField(max_length=200)
    slug=models.SlugField(max_length=140,unique=True,blank=True)
    description=models.TextField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active= models.BooleanField(default=True)
    sort_order=models.PositiveIntegerField(default=0)
    image=models.ImageField(upload_to='categories/%Y/%m/%d/',blank=True,null=True)
    is_featured=models.BooleanField(default=False)


    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug=slugify(self.name)
        super().save(*args,**kwargs)


    def __str__(self):
        return self.name
class Brand(models.Model):
    name=models.CharField(max_length=50)
    image=models.ImageField(upload_to='brand/%Y/%m/%d/',blank=True,null=True)
    def __str__(self):
        return self.name

class Color(models.Model):
    name=models.CharField(max_length=50)
    def __str__(self):
        return self.name
class Size(models.Model):
    name=models.CharField(max_length=50)
    def __str__(self):
        return self.name
#مدل محصول
class Product(models.Model):
    name=models.CharField(max_length=200)
    description=models.TextField()
    price=models.DecimalField(decimal_places=2,max_digits=12)
    stock_quantity=models.PositiveIntegerField()
    image=models.ImageField(upload_to='photo/%Y/%m/%d/')
    slug=models.SlugField(max_length=140,unique=True)
    is_available=models.BooleanField(default=True)
    updated_at=models.DateTimeField(auto_now=True)
    created_at=models.DateTimeField(auto_now_add=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name="products",)
    discount_percentage=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    is_featured=models.BooleanField(default=False)
    minimum_stock=models.PositiveIntegerField()
    brands=models.ManyToManyField(Brand,blank=True)
    colors=models.ManyToManyField(Color,blank=True)
    sizes = models.ManyToManyField(Size, blank=True)
    GENDER_CHOICES = [
        ('male', 'مردانه'),
        ('female', 'زنانه')
    ]
    gender=models.CharField(max_length=10,choices=GENDER_CHOICES,default='male')

    @property
    def discounted_price(self):
        if self.discount_percentage>0:
            discount_amount=self.price*self.discount_percentage/100
            return self.price-discount_amount
        else:
            return self.price


    def __str__(self):
        return self.name
    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug=slugify(self.name)
        super().save(*args,**kwargs)

class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name="gallery")
    image=models.ImageField(upload_to='photo/%Y/%m/%d/')
    alt_text=models.CharField(max_length=100,blank=True)
    def __str__(self):
        return f"{self.product.name}-image"
#مدل برای امتیاز دهی
class Rating(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey('shop.Product',on_delete=models.CASCADE,related_name='ratings')
    score=models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1),MaxValueValidator(5)]
    )
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together=('user','product')
    def __str__(self):
        return f"{self.user.username}rated {self.product.name} with {self.score}"
    #ساخت بنر اسلایدی صفحه اصلی
class Banner(models.Model):
    image=models.ImageField(upload_to='banners/%Y/%m/%d/',verbose_name='تصویر')
    title=models.CharField(max_length=200,verbose_name='عنوان')
    description=models.TextField(blank=True,verbose_name='توضیحات')
    is_active=models.BooleanField(default=True,verbose_name='فعال')
    created_at=models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ویرایش')
    order=models.PositiveIntegerField(default=0,verbose_name='ترتیب نمایش')
    subtitle=models.CharField(max_length=200,blank=True,verbose_name='زیر عنوان')

    class Meta:
        verbose_name='بنر'
        verbose_name_plural='بنرها'
        ordering=['order','-created_at']
    def __str__(self):
        return self.title

  #دریافت پیام/تماس با ما
class ContactMessage(models.Model):
    first_last_name=models.CharField(max_length=200,verbose_name='نام و نام خانوادگی')
    email=models.EmailField(verbose_name='ایمیل')
    subject=models.CharField(max_length=200,blank=True,verbose_name='موضوع')
    message=models.TextField(verbose_name='پیام')
    created_at=models.DateTimeField(auto_now_add=True,verbose_name='تاریخ ثبت')
    is_read=models.BooleanField(default=False,verbose_name='خوانده شده')

    class Meta:
        verbose_name='پیام تماس'
        verbose_name_plural='پیام های تماس'
    def __str__(self):
        return f"{self.first_last_name} ({self.email}) - {self.created_at:%Y-%m-%d}"