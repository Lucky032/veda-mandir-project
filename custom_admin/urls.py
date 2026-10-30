from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    # Dashboard
    path('', views.admin_dashboard, name='dashboard'),
    
    # Pujas Management
    path('pujas/', views.puja_list, name='puja_list'),
    path('pujas/add/', views.puja_add, name='puja_add'),
    path('pujas/edit/<int:puja_id>/', views.puja_edit, name='puja_edit'),
    path('pujas/delete/<int:puja_id>/', views.puja_delete, name='puja_delete'),
    
    # Bookings Management
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/view/<int:booking_id>/', views.booking_view, name='booking_view'),
    path('bookings/update-status/<int:booking_id>/', views.booking_update_status, name='booking_update_status'),
    
    # Payments Management
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/view/<int:payment_id>/', views.payment_view, name='payment_view'),
    
    # Users Management
    path('users/', views.user_list, name='user_list'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/edit/<int:category_id>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:category_id>/', views.category_delete, name='category_delete'),
]
