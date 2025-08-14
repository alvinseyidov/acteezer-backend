#!/usr/bin/env python
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User

# Create superuser
phone = '+994505815696'
first_name = 'Admin'
last_name = 'User'
password = 'admin123'  # You should change this password

try:
    # Check if user already exists
    if User.objects.filter(phone=phone).exists():
        user = User.objects.get(phone=phone)
        # Update existing user to superuser
        user.is_staff = True
        user.is_superuser = True
        user.is_phone_verified = True
        user.is_registration_complete = True
        user.registration_step = 8
        user.save()
        print(f"Updated existing user {phone} to superuser status")
    else:
        # Create new superuser
        user = User.objects.create_superuser(
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        print(f"Created new superuser with phone: {phone}")
        print(f"Password: {password}")
        print("Please change the password after first login!")

except Exception as e:
    print(f"Error creating superuser: {e}")
