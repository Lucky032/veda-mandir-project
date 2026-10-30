from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:puja_id>/', views.create_booking, name='create_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('success/<int:booking_id>/', views.booking_success, name='booking_success'),
]
