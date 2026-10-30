from django.db import models
from django.contrib.auth.models import User
from pujas.models import Puja


class Booking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ]

    # Relations
    puja = models.ForeignKey(Puja, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    
    # Customer Details (These are the missing fields!)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    
    # Booking Details
    booking_date = models.DateField()
    special_requests = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'

    def __str__(self):
        return f"Booking {self.id} - {self.puja.name} - {self.customer_name}"
    
    @property
    def is_paid(self):
        """Check if booking is paid"""
        return self.payment_status == 'paid'
    
    @property
    def status_badge_class(self):
        """Return Bootstrap badge class for status"""
        status_classes = {
            'pending': 'warning',
            'confirmed': 'success',
            'completed': 'primary',
            'cancelled': 'danger',
        }
        return status_classes.get(self.status, 'secondary')
