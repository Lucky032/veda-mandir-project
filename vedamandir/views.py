from django.shortcuts import render
from pujas.models import Puja, PujaCategory

def home(request):
    """Homepage view showing featured pujas"""
    featured_pujas = Puja.objects.filter(is_active=True)[:6]
    categories = PujaCategory.objects.all()
    
    context = {
        'featured_pujas': featured_pujas,
        'categories': categories,
    }
    return render(request, 'home.html', context)

def about(request):
    """About page view"""
    return render(request, 'about.html')
