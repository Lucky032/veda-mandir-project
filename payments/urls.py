from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<int:booking_id>/', views.initiate_payment, name='initiate_payment'),
    path('confirm/<int:payment_id>/', views.confirm_payment, name='confirm_payment'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
]
