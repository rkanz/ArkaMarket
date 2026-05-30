from .models import Category,Brand

def categories_processor(request):
    try:
        categories = Category.objects.all()
        return {
            'categories': categories
        }
    except Exception as e:
        print(f"Error in categories_processor : {e}")
        return {'categories':[]}

def brands_processor(request):
    try:
        brands=list(Brand.objects.all())
        all_brands=[brands[i:i+4]for i in range(0,len(brands),4)]
        return {
            'all_brands': all_brands
        }
    except Exception as e:
        print(f"Error in brands_processor : {e}")
        return {'brands':[]}