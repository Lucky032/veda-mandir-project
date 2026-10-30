from django.urls import path
from . import views

app_name = 'pujas'

urlpatterns = [
    path('', views.puja_list, name='puja_list'),
    path('<int:pk>/', views.puja_detail, name='puja_detail'),
]
