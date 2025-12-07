"""
Custom adapters for django-allauth to handle Google OAuth
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter for handling standard account operations"""
    
    def get_login_redirect_url(self, request):
        """Redirect after login based on registration status"""
        user = request.user
        if user.is_authenticated:
            if not user.is_registration_complete:
                # Redirect to continue registration
                return reverse('accounts:full_name_registration')
            return '/'
        return '/'
    
    def save_user(self, request, user, form, commit=True):
        """Save user data from signup form"""
        user = super().save_user(request, user, form, commit=False)
        if commit:
            user.save()
        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter for handling Google OAuth"""
    
    def pre_social_login(self, request, sociallogin):
        """
        Called before social login. Check if user already exists with this email.
        If so, connect the social account to the existing user.
        """
        # If social login is already connected to a user, do nothing
        if sociallogin.is_existing:
            return
        
        # Check if there's an existing user with this email
        email = sociallogin.account.extra_data.get('email')
        if email:
            from accounts.models import User
            try:
                user = User.objects.get(email=email)
                # Connect the social account to the existing user
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass
    
    def populate_user(self, request, sociallogin, data):
        """
        Populate user data from social provider.
        Gets first name, last name, and email from Google.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Get data from Google
        extra_data = sociallogin.account.extra_data
        
        user.first_name = extra_data.get('given_name', data.get('first_name', ''))
        user.last_name = extra_data.get('family_name', data.get('last_name', ''))
        user.email = extra_data.get('email', data.get('email', ''))
        
        # Set a flag that this is a Google signup (no phone required)
        user.is_google_signup = True
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save the user from social login.
        Skip phone requirement for Google signups.
        """
        user = sociallogin.user
        
        # Generate a unique phone placeholder for Google users (since phone is required)
        # We'll use the Google ID as a placeholder
        if not user.phone:
            google_id = sociallogin.account.extra_data.get('sub', sociallogin.account.uid)
            user.phone = f'+000{google_id[:12]}'  # Placeholder phone
        
        # Mark as Google signup
        user.is_google_signup = True
        user.is_phone_verified = True  # Skip phone verification for Google users
        user.registration_step = 1  # Start from name step
        
        user.save()
        sociallogin.save(request)
        
        return user
    
    def get_connect_redirect_url(self, request, socialaccount):
        """Redirect after connecting social account"""
        return '/'
    
    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """Handle authentication errors"""
        from django.contrib import messages
        messages.error(request, 'Google ilə giriş zamanı xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.')
        return redirect('accounts:phone_registration')

