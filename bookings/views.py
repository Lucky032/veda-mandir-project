from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from pujas.models import Puja
from .models import Booking

def create_booking(request, puja_id):
    """Create a new booking"""
    puja = get_object_or_404(Puja, pk=puja_id, is_active=True)
    
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        date = request.POST.get('booking_date')
        special_requests = request.POST.get('special_requests', '')
        
        # Create booking
        booking = Booking.objects.create(
            puja=puja,
            user=request.user if request.user.is_authenticated else None,
            customer_name=name,
            customer_email=email,
            customer_phone=phone,
            booking_date=date,
            special_requests=special_requests,
            total_amount=puja.price,
            status='pending'
        )
        
        messages.success(request, 'Booking created successfully!')
        return redirect('bookings:booking_success', booking_id=booking.id)
    
    context = {
        'puja': puja,
    }
    return render(request, 'bookings/create_booking.html', context)

def booking_success(request, booking_id):
    """Booking confirmation page"""
    booking = get_object_or_404(Booking, pk=booking_id)
    
    context = {
        'booking': booking,
    }
    return render(request, 'bookings/booking_success.html', context)

@login_required
def my_bookings(request):
    """Display user's bookings"""
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'bookings': bookings,
    }
    return render(request, 'bookings/my_bookings.html', context)
