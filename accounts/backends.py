from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class SuperuserEmailBackend(ModelBackend):
    """
    Custom authentication backend that allows superusers to login with email and password
    Regular users still authenticate with phone number
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        if username is None or password is None:
            return None
        
        try:
            # Check if the username looks like an email
            if '@' in username:
                # Try to find a superuser with this email
                user = User.objects.get(
                    Q(email__iexact=username) & Q(is_superuser=True)
                )
            else:
                # Regular phone-based authentication
                user = User.objects.get(**{User.USERNAME_FIELD: username})
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
        return user if self.user_can_authenticate(user) else None
