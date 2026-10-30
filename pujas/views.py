from django.shortcuts import render, get_object_or_404
from .models import Puja, PujaCategory

def puja_list(request):
    """Display all pujas"""
    pujas = Puja.objects.filter(is_active=True)
    categories = PujaCategory.objects.all()
    
    context = {
        'pujas': pujas,
        'categories': categories,
    }
    return render(request, 'pujas/puja_list.html', context)

def puja_detail(request, pk):
    """Display single puja details"""
    puja = get_object_or_404(Puja, pk=pk, is_active=True)
    
    context = {
        'puja': puja,
    }
    return render(request, 'pujas/puja_detail.html', context)
