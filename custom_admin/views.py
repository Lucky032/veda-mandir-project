from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .decorators import admin_required
from pujas.models import Puja, PujaCategory
from bookings.models import Booking
from payments.models import Payment
from django.contrib.auth.models import User


@admin_required
def admin_dashboard(request):
    """Admin Dashboard with statistics"""
    # Get statistics
    total_pujas = Puja.objects.count()
    total_bookings = Booking.objects.count()
    total_revenue = Payment.objects.filter(payment_status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    total_users = User.objects.count()
    
    # Recent bookings
    recent_bookings = Booking.objects.select_related('puja', 'user').order_by('-created_at')[:10]
    
    # Pending bookings
    pending_bookings = Booking.objects.filter(status='pending').count()
    
    # This month statistics
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_bookings = Booking.objects.filter(created_at__gte=current_month).count()
    month_revenue = Payment.objects.filter(
        payment_status='completed', 
        created_at__gte=current_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Popular pujas
    popular_pujas = Puja.objects.annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:5]
    
    context = {
        'total_pujas': total_pujas,
        'total_bookings': total_bookings,
        'total_revenue': total_revenue,
        'total_users': total_users,
        'recent_bookings': recent_bookings,
        'pending_bookings': pending_bookings,
        'month_bookings': month_bookings,
        'month_revenue': month_revenue,
        'popular_pujas': popular_pujas,
    }
    
    return render(request, 'custom_admin/dashboard.html', context)


@admin_required
def puja_list(request):
    """List all pujas"""
    pujas = Puja.objects.select_related('category').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        pujas = pujas.filter(
            Q(name__icontains=search_query) | 
            Q(name_te__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'pujas': pujas,
        'search_query': search_query,
    }
    
    return render(request, 'custom_admin/puja_list.html', context)


@admin_required
def puja_add(request):
    """Add new puja"""
    if request.method == 'POST':
        name = request.POST.get('name')
        name_te = request.POST.get('name_te')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        description_te = request.POST.get('description_te')
        price = request.POST.get('price')
        duration = request.POST.get('duration')
        benefits = request.POST.get('benefits')
        requirements = request.POST.get('requirements')
        is_active = request.POST.get('is_active') == 'on'
        featured = request.POST.get('featured') == 'on'
        image = request.FILES.get('image')
        
        category = None
        if category_id:
            category = PujaCategory.objects.get(id=category_id)
        
        puja = Puja.objects.create(
            name=name,
            name_te=name_te,
            category=category,
            description=description,
            description_te=description_te,
            price=price,
            duration=duration,
            benefits=benefits,
            requirements=requirements,
            is_active=is_active,
            featured=featured,
            image=image
        )
        
        messages.success(request, f'Puja "{name}" added successfully!')
        return redirect('custom_admin:puja_list')
    
    categories = PujaCategory.objects.all()
    context = {'categories': categories}
    return render(request, 'custom_admin/puja_form.html', context)


@admin_required
def puja_edit(request, puja_id):
    """Edit existing puja"""
    puja = get_object_or_404(Puja, id=puja_id)
    
    if request.method == 'POST':
        puja.name = request.POST.get('name')
        puja.name_te = request.POST.get('name_te')
        category_id = request.POST.get('category')
        puja.description = request.POST.get('description')
        puja.description_te = request.POST.get('description_te')
        puja.price = request.POST.get('price')
        puja.duration = request.POST.get('duration')
        puja.benefits = request.POST.get('benefits')
        puja.requirements = request.POST.get('requirements')
        puja.is_active = request.POST.get('is_active') == 'on'
        puja.featured = request.POST.get('featured') == 'on'
        
        if category_id:
            puja.category = PujaCategory.objects.get(id=category_id)
        
        if request.FILES.get('image'):
            puja.image = request.FILES.get('image')
        
        puja.save()
        
        messages.success(request, f'Puja "{puja.name}" updated successfully!')
        return redirect('custom_admin:puja_list')
    
    categories = PujaCategory.objects.all()
    context = {
        'puja': puja,
        'categories': categories,
        'edit_mode': True
    }
    return render(request, 'custom_admin/puja_form.html', context)


@admin_required
def puja_delete(request, puja_id):
    """Delete puja"""
    puja = get_object_or_404(Puja, id=puja_id)
    puja_name = puja.name
    puja.delete()
    messages.success(request, f'Puja "{puja_name}" deleted successfully!')
    return redirect('custom_admin:puja_list')


@admin_required
def booking_list(request):
    """List all bookings"""
    bookings = Booking.objects.select_related('puja', 'user').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        bookings = bookings.filter(
            Q(customer_name__icontains=search_query) |
            Q(customer_email__icontains=search_query) |
            Q(customer_phone__icontains=search_query) |
            Q(puja__name__icontains=search_query)
        )
    
    context = {
        'bookings': bookings,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'custom_admin/booking_list.html', context)


@admin_required
def booking_view(request, booking_id):
    """View booking details"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    context = {
        'booking': booking,
    }
    
    return render(request, 'custom_admin/booking_view.html', context)


@admin_required
def booking_update_status(request, booking_id):
    """Update booking status"""
    if request.method == 'POST':
        booking = get_object_or_404(Booking, id=booking_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Booking.BOOKING_STATUS).keys():
            booking.status = new_status
            booking.save()
            messages.success(request, f'Booking status updated to {new_status}!')
        else:
            messages.error(request, 'Invalid status!')
    
    return redirect('custom_admin:booking_view', booking_id=booking_id)


@admin_required
def payment_list(request):
    """List all payments"""
    payments = Payment.objects.select_related('booking', 'user').order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        payments = payments.filter(payment_status=status_filter)
    
    context = {
        'payments': payments,
        'status_filter': status_filter,
    }
    
    return render(request, 'custom_admin/payment_list.html', context)


@admin_required
def payment_view(request, payment_id):
    """View payment details"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'custom_admin/payment_view.html', context)


@admin_required
def user_list(request):
    """List all users"""
    users = User.objects.order_by('-date_joined')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    context = {
        'users': users,
        'search_query': search_query,
    }
    
    return render(request, 'custom_admin/user_list.html', context)


@admin_required
def category_list(request):
    """List all categories"""
    categories = PujaCategory.objects.annotate(
        puja_count=Count('puja')
    ).order_by('-created_at')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'custom_admin/category_list.html', context)


@admin_required
def category_add(request):
    """Add new category"""
    if request.method == 'POST':
        name = request.POST.get('name')
        name_te = request.POST.get('name_te')
        description = request.POST.get('description')
        description_te = request.POST.get('description_te')
        
        category = PujaCategory.objects.create(
            name=name,
            name_te=name_te,
            description=description,
            description_te=description_te
        )
        
        messages.success(request, f'Category "{name}" added successfully!')
        return redirect('custom_admin:category_list')
    
    return render(request, 'custom_admin/category_form.html')


@admin_required
def category_edit(request, category_id):
    """Edit existing category"""
    category = get_object_or_404(PujaCategory, id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.name_te = request.POST.get('name_te')
        category.description = request.POST.get('description')
        category.description_te = request.POST.get('description_te')
        category.save()
        
        messages.success(request, f'Category "{category.name}" updated successfully!')
        return redirect('custom_admin:category_list')
    
    context = {
        'category': category,
        'edit_mode': True
    }
    return render(request, 'custom_admin/category_form.html', context)


@admin_required
def category_delete(request, category_id):
    """Delete category"""
    category = get_object_or_404(PujaCategory, id=category_id)
    category_name = category.name
    category.delete()
    messages.success(request, f'Category "{category_name}" deleted successfully!')
    return redirect('custom_admin:category_list')
