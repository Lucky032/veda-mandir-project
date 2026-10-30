from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from bookings.models import Booking
from .models import Payment


# @login_required
def initiate_payment(request, booking_id):
    """Initiate UPI payment"""
    booking = get_object_or_404(Booking, pk=booking_id)
    
    # Check if payment already exists for this booking
    try:
        payment = Payment.objects.get(booking=booking)
        # If payment exists but is pending, show payment page
        if payment.payment_status == 'pending':
            context = {
                'booking': booking,
                'payment': payment,
                'upi_id': settings.UPI_ID,
                'upi_name': settings.UPI_NAME,
            }
            return render(request, 'payments/upi_payment.html', context)
        # If already completed, redirect to success
        elif payment.payment_status == 'completed':
            messages.info(request, 'This booking is already paid!')
            return redirect('payments:payment_success', payment_id=payment.id)
    except Payment.DoesNotExist:
        # Create new payment record only if doesn't exist
        payment = Payment.objects.create(
            booking=booking,
            user=request.user,
            amount=booking.total_amount,
            payment_method='upi',
            payment_status='pending'
        )
    
    context = {
        'booking': booking,
        'payment': payment,
        'upi_id': settings.UPI_ID,
        'upi_name': settings.UPI_NAME,
    }
    return render(request, 'payments/upi_payment.html', context)


# @login_required
def confirm_payment(request, payment_id):
    """Confirm UPI payment with transaction ID"""
    payment = get_object_or_404(Payment, pk=payment_id)
    
    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        
        if transaction_id:
            # Update payment
            payment.transaction_id = transaction_id
            payment.payment_status = 'completed'
            payment.save()
            
            # Update booking
            booking = payment.booking
            booking.payment_status = 'paid'
            booking.status = 'confirmed'
            booking.save()
            
            messages.success(request, 'Payment confirmed! Your booking is confirmed.')
            return redirect('payments:payment_success', payment_id=payment.id)
        else:
            messages.error(request, 'Please enter UPI transaction ID')
    
    return redirect('payments:initiate_payment', booking_id=payment.booking.id)


# @login_required
def payment_success(request, payment_id):
    """Payment success page"""
    payment = get_object_or_404(Payment, pk=payment_id)
    
    context = {
        'payment': payment,
        'booking': payment.booking,
    }
    return render(request, 'payments/payment_success.html', context)


# @login_required
def payment_failed(request):
    """Payment failed page"""
    return render(request, 'payments/payment_failed.html')
