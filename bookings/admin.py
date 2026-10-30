from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'puja', 'customer_name', 'booking_date', 'status', 'payment_status', 'total_amount', 'created_at']
    list_filter = ['status', 'booking_date', 'payment_status', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'customer_phone', 'puja__name']
    list_editable = ['status', 'payment_status']
    date_hierarchy = 'booking_date'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Puja Information', {
            'fields': ('puja', 'user')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Booking Details', {
            'fields': ('booking_date', 'total_amount', 'special_requests')
        }),
        ('Status', {
            'fields': ('status', 'payment_status')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing booking
            return self.readonly_fields + ['puja', 'total_amount']
        return self.readonly_fields
