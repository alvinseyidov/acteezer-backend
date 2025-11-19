from django.core.management.base import BaseCommand
from activities.models import Activity
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time


class Command(BaseCommand):
    help = 'Update latitude and longitude for activities that have addresses but missing coordinates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update all activities, even those with existing coordinates',
        )
        parser.add_argument(
            '--city',
            type=str,
            default='Baku, Azerbaijan',
            help='Default city to append to addresses (default: Baku, Azerbaijan)',
        )

    def handle(self, *args, **options):
        force_update = options['force']
        default_city = options['city']
        
        # Initialize geocoder
        geolocator = Nominatim(user_agent="acteezer_location_updater")
        
        # Get activities that need coordinates
        if force_update:
            activities = Activity.objects.all()
            self.stdout.write(self.style.WARNING(f'Force updating all {activities.count()} activities...'))
        else:
            activities = Activity.objects.filter(latitude__isnull=True) | Activity.objects.filter(longitude__isnull=True)
            self.stdout.write(self.style.WARNING(f'Found {activities.count()} activities without coordinates...'))
        
        updated_count = 0
        failed_count = 0
        
        for activity in activities:
            try:
                # Try different address formats
                addresses_to_try = []
                
                # 1. Full address with city
                if activity.address:
                    addresses_to_try.append(f"{activity.address}, {default_city}")
                
                # 2. Location name with city
                if activity.location_name:
                    addresses_to_try.append(f"{activity.location_name}, {default_city}")
                
                # 3. District with city
                if activity.district:
                    addresses_to_try.append(f"{activity.district}, {default_city}")
                
                # 4. Just the city
                addresses_to_try.append(default_city)
                
                location = None
                for address in addresses_to_try:
                    try:
                        self.stdout.write(f'Trying to geocode: {address}')
                        location = geolocator.geocode(address, timeout=10)
                        if location:
                            break
                        time.sleep(1)  # Rate limiting
                    except (GeocoderTimedOut, GeocoderServiceError) as e:
                        self.stdout.write(self.style.WARNING(f'  Error: {str(e)}'))
                        time.sleep(2)
                        continue
                
                if location:
                    activity.latitude = location.latitude
                    activity.longitude = location.longitude
                    activity.save(update_fields=['latitude', 'longitude'])
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Updated "{activity.title}": ({location.latitude}, {location.longitude})'
                        )
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Could not geocode "{activity.title}" - Address: {activity.address or activity.location_name}'
                        )
                    )
                    failed_count += 1
                
                # Rate limiting to avoid being blocked
                time.sleep(1)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Error processing "{activity.title}": {str(e)}')
                )
                failed_count += 1
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'Successfully updated: {updated_count} activities'))
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f'Failed to update: {failed_count} activities'))
        self.stdout.write('='*60)

