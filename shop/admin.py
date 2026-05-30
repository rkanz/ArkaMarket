from django.contrib import admin
from .models import Product, Color, Size,ProductImage,Brand
from . models import Category,Banner,ContactMessage

# Register your models here.
class ProductImageInline(admin.TabularInline):
    model=ProductImage
    extra=1

class ProductAdmin(admin.ModelAdmin):
    inlines=[ProductImageInline]
    list_display=('id','name','stock_quantity','updated_at','created_at','is_available','is_featured'
                      ,'category','discount_percentage','get_colors','get_sizes','get_brands','gender')
    list_filter=['category','gender']
    list_display_links=['id','name']
    list_editable=['is_available','is_featured']
    list_per_page=20
    search_fields=['name','category__name','text','brands__name','gender']

    def get_colors(self,obj):
        return ",".join([str(c.name)for c in obj.colors.all()])
    get_colors.short_description='colors'

    def get_sizes(self,obj):
        return",".join([str(s.name) for s in obj.sizes.all()])
    get_sizes.short_description='sizes'

    def get_brands(self, obj):
        return ",".join([str(b.name) for b in obj.brands.all()])
    get_brands.short_description = 'brands'

admin.site.register(Product,ProductAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display=('id','name','created_at','updated_at','is_active','is_featured','sort_order')
    list_display_links=['id','name']
    list_editable=['is_active','sort_order','is_featured']
    search_fields=['name']
    list_per_page=20
admin.site.register(Category,CategoryAdmin)

class BrandAdmin(admin.ModelAdmin):
    list_display=['name']
admin.site.register(Brand,BrandAdmin)

class ColorAdmin(admin.ModelAdmin):
    list_display=['name']
admin.site.register(Color,ColorAdmin)

class SizeAdmin(admin.ModelAdmin):
    list_display=['name']
admin.site.register(Size,SizeAdmin)

class BannerAdmin(admin.ModelAdmin):
    list_display=('title','is_active','created_at','order')
    list_display_link=['title']
    list_editable=['is_active','order']
    ordering=('order',)
    search_field=['title','subtitle','description']
    list_per_page=20
admin.site.register(Banner,BannerAdmin)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display=('first_last_name','email','subject','created_at','is_read')
    list_display_links=('email','subject','first_last_name')
    list_editable=['is_read']
    ordering=('-created_at',)
    readonly_fields=('created_at','email','subject','first_last_name','message')
    search_fields=['first_last_name','subject','email','message']

