from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from datetime import timedelta
import random
import string


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    gotra = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Password reset fields
    reset_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - Profile"
    
    def generate_otp(self):
        """Generate 6-digit OTP"""
        self.reset_otp = ''.join(random.choices(string.digits, k=6))
        self.otp_created_at = timezone.now()
        self.save()
        return self.reset_otp
    
    def verify_otp(self, otp):
        """Verify OTP is valid and not expired (15 minutes)"""
        if not self.reset_otp or not self.otp_created_at:
            return False
        if self.reset_otp != otp:
            return False
        if timezone.now() > self.otp_created_at + timedelta(minutes=15):
            return False
        return True


class PasswordHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_history')
    password_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - Password changed on {self.created_at}"
    
    @staticmethod
    def check_password_reuse(user, new_password, history_count=5):
        """Check if password was used in last 5 passwords"""
        recent_passwords = PasswordHistory.objects.filter(user=user)[:history_count]
        for history in recent_passwords:
            if check_password(new_password, history.password_hash):
                return True
        # Also check current password
        if user.check_password(new_password):
            return True
        return False
    
    @staticmethod
    def add_password_history(user):
        """Add current password to history"""
        PasswordHistory.objects.create(
            user=user,
            password_hash=user.password  # Already hashed by Django
        )
