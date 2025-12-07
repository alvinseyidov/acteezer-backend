"""
Middleware for handling registration flow
"""
from django.shortcuts import redirect
from django.urls import reverse


class RegistrationCompleteMiddleware:
    """
    Middleware to redirect users who haven't completed registration
    to the appropriate registration step.
    """
    
    # URLs that should be accessible without completing registration
    ALLOWED_URLS = [
        '/accounts/register/',
        '/accounts/register/phone/',
        '/accounts/register/otp/',
        '/accounts/register/name/',
        '/accounts/register/languages/',
        '/accounts/register/birthday/',
        '/accounts/register/images/',
        '/accounts/register/bio/',
        '/accounts/register/interests/',
        '/accounts/register/location/',
        '/accounts/register/complete/',
        '/accounts/logout/',
        '/accounts/social/',
        '/admin/',
        '/static/',
        '/media/',
        '/i18n/',
        '/terms/',
        '/privacy/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if user is authenticated but hasn't completed registration
        if request.user.is_authenticated:
            if not request.user.is_registration_complete:
                # Check if current URL is allowed
                path = request.path
                is_allowed = any(path.startswith(url) for url in self.ALLOWED_URLS)
                
                if not is_allowed:
                    # Redirect to the appropriate registration step
                    step = request.user.registration_step
                    
                    if step <= 2:
                        return redirect('accounts:full_name_registration')
                    elif step == 3:
                        return redirect('accounts:languages_registration')
                    elif step == 4:
                        return redirect('accounts:birthday_registration')
                    elif step == 5:
                        return redirect('accounts:images_registration')
                    elif step == 6:
                        return redirect('accounts:bio_registration')
                    elif step == 7:
                        return redirect('accounts:interests_registration')
                    elif step == 8:
                        return redirect('accounts:location_registration')
                    else:
                        return redirect('accounts:full_name_registration')
        
        response = self.get_response(request)
        return response

