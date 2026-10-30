from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile, PasswordHistory
from difflib import SequenceMatcher


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now login.')
            return redirect('users:login')
    else:
        form = UserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


def user_login(request):
    """User login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    """User profile view"""
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    
    if request.method == 'POST':
        # Update profile
        user_profile.phone = request.POST.get('phone')
        user_profile.address = request.POST.get('address')
        user_profile.city = request.POST.get('city')
        user_profile.state = request.POST.get('state')
        user_profile.pincode = request.POST.get('pincode')
        user_profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('users:profile')
    
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'users/profile.html', context)


# ============ PASSWORD RESET VIEWS ============

def request_password_reset(request):
    """Step 1: User enters email to receive OTP"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Get or create UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Generate OTP
            otp = profile.generate_otp()
            
            # Send OTP email
            subject = 'Password Reset Code - Veda Mandir'
            message = f'''
नमस्ते {user.first_name or user.username},

Your password reset code is: {otp}

This code will expire in 15 minutes.

If you didn't request this, please ignore this email.

With Regards,
Veda Mandir Team 🕉️
            '''
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                request.session['reset_email'] = email
                messages.success(request, 'Reset code sent to your email! Check your inbox.')
                return redirect('users:verify_otp')
            except Exception as e:
                messages.error(request, f'Failed to send email. Please try again later.')
                print(f"Email error: {e}")
        
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address!')
    
    return render(request, 'users/request_reset.html')


def verify_otp(request):
    """Step 2: User enters OTP code"""
    if 'reset_email' not in request.session:
        messages.warning(request, 'Please start the password reset process.')
        return redirect('users:request_password_reset')
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        email = request.session.get('reset_email')
        
        try:
            user = User.objects.get(email=email)
            profile = UserProfile.objects.get(user=user)
            
            if profile.verify_otp(otp):
                request.session['verified_user_id'] = user.id
                messages.success(request, 'OTP verified successfully! Now set your new password.')
                return redirect('users:reset_password')
            else:
                messages.error(request, 'Invalid or expired OTP! Please try again.')
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            messages.error(request, 'User not found!')
    
    return render(request, 'users/verify_otp.html')


def reset_password(request):
    """Step 3: User sets new password"""
    if 'verified_user_id' not in request.session:
        messages.warning(request, 'Please complete OTP verification first.')
        return redirect('users:request_password_reset')
    
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        user_id = request.session.get('verified_user_id')
        
        try:
            user = User.objects.get(id=user_id)
            profile = UserProfile.objects.get(user=user)
            
            # Validation 1: Check if passwords match
            if password1 != password2:
                messages.error(request, 'Passwords do not match!')
                return render(request, 'users/reset_password.html')
            
            # Validation 2: Minimum length
            if len(password1) < 8:
                messages.error(request, 'Password must be at least 8 characters long!')
                return render(request, 'users/reset_password.html')
            
            # Validation 3: Check if same as current password
            if user.check_password(password1):
                messages.error(request, 'New password cannot be the same as your current password!')
                return render(request, 'users/reset_password.html')
            
            # Validation 4: Check password reuse from history
            if PasswordHistory.check_password_reuse(user, password1, history_count=5):
                messages.error(request, 'You cannot reuse any of your last 5 passwords!')
                return render(request, 'users/reset_password.html')
            
            # Validation 5: Check similarity with username
            similarity = SequenceMatcher(None, password1.lower(), user.username.lower()).ratio()
            if similarity > 0.7:
                messages.error(request, 'Password is too similar to your username!')
                return render(request, 'users/reset_password.html')
            
            # Validation 6: Check similarity with email
            email_name = user.email.split('@')[0] if user.email else ''
            if email_name:
                similarity = SequenceMatcher(None, password1.lower(), email_name.lower()).ratio()
                if similarity > 0.7:
                    messages.error(request, 'Password is too similar to your email!')
                    return render(request, 'users/reset_password.html')
            
            # Save current password to history before changing
            PasswordHistory.add_password_history(user)
            
            # Set new password
            user.set_password(password1)
            user.save()
            
            # Clear OTP
            profile.reset_otp = None
            profile.otp_created_at = None
            profile.save()
            
            # Clear session
            del request.session['reset_email']
            del request.session['verified_user_id']
            
            messages.success(request, 'Password reset successful! Please login with your new password.')
            return redirect('users:login')
            
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            messages.error(request, 'User not found!')
    
    return render(request, 'users/reset_password.html')
