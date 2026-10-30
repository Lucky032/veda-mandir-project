from django.contrib import admin
from .models import Puja, PujaCategory

@admin.register(PujaCategory)
class PujaCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Puja)
class PujaAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'duration', 'is_active', 'featured', 'created_at']
    list_filter = ['category', 'is_active', 'featured']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'featured']
