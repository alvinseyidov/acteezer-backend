from django.core.management.base import BaseCommand
from django.core.management import CommandError
from accounts.models import User


class Command(BaseCommand):
    help = 'Creates a superuser with phone +994505815696 and email for admin access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='admin@acteezer.com',
            help='Email address for the superuser (default: admin@acteezer.com)',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the superuser (if not provided, you will be prompted)',
        )

    def handle(self, *args, **options):
        phone = '+994505815696'
        email = options['email']
        password = options['password']
        
        # Check if user already exists
        try:
            user = User.objects.get(phone=phone)
            self.stdout.write(
                self.style.WARNING(f'User with phone {phone} already exists. Updating with email and superuser privileges...')
            )
            
            # Update existing user
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_phone_verified = True
            user.is_registration_complete = True
            user.registration_step = 8
            
            if password:
                user.set_password(password)
                self.stdout.write(self.style.SUCCESS('Password updated.'))
            
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated user {phone} with email {email}'))
            
        except User.DoesNotExist:
            # Create new superuser
            if not password:
                import getpass
                password = getpass.getpass('Password: ')
                if not password:
                    raise CommandError('Password is required')
            
            user = User.objects.create_superuser(
                phone=phone,
                first_name='Admin',
                last_name='User',
                password=password,
                email=email
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created superuser with phone {phone} and email {email}')
            )
        
        # Display login instructions
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Superuser setup complete!'))
        self.stdout.write('')
        self.stdout.write('You can now login to Django admin with either:')
        self.stdout.write(f'  1. Phone: {phone} + password')
        self.stdout.write(f'  2. Email: {email} + password (superuser only)')
        self.stdout.write('')
        self.stdout.write('Admin URL: http://localhost:8000/admin/')
