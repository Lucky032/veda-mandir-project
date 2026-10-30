from django.db import models
from django.contrib.auth.models import User

class PujaCategory(models.Model):
    name = models.CharField(max_length=100)
    name_te = models.CharField(max_length=100, blank=True, null=True) 
    description = models.TextField(blank=True)
    description_te = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Puja Categories"

    def __str__(self):
        return self.name


class Puja(models.Model):
    name = models.CharField(max_length=200)
    name_te = models.CharField(max_length=200, blank=True, null=True) 
    category = models.ForeignKey(PujaCategory, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    description_te = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=100, help_text="e.g., 2-3 hours")
    image = models.ImageField(upload_to='pujas/', blank=True, null=True)
    benefits = models.TextField(help_text="Benefits of this puja")
    requirements = models.TextField(help_text="What's required from user", blank=True)
    is_active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Pujas"

    def __str__(self):
        return self.name
