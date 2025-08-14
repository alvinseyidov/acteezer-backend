from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from activities.models import ActivityCategory, Activity
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample activities data for demonstration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample activities data...'))

        # Get or create a superuser as organizer
        try:
            organizer = User.objects.filter(is_superuser=True).first()
            if not organizer:
                organizer = User.objects.create_superuser(
                    phone='+994501234567',
                    first_name='Acteezer',
                    last_name='Admin',
                    email='admin@acteezer.az',
                    password='admin123'
                )
                self.stdout.write(f'Created organizer: {organizer.get_full_name()}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating organizer: {e}'))
            return

        # Create categories
        categories_data = [
            {'name': 'İdman', 'category_type': 'sports', 'icon': 'fas fa-running', 'color': '#ef4444'},
            {'name': 'Mədəniyyət', 'category_type': 'culture', 'icon': 'fas fa-theater-masks', 'color': '#8b5cf6'},
            {'name': 'Təbiət', 'category_type': 'nature', 'icon': 'fas fa-tree', 'color': '#22c55e'},
            {'name': 'Sənət', 'category_type': 'art', 'icon': 'fas fa-palette', 'color': '#f59e0b'},
            {'name': 'Yemək', 'category_type': 'food', 'icon': 'fas fa-utensils', 'color': '#ec4899'},
            {'name': 'Təhsil', 'category_type': 'education', 'icon': 'fas fa-graduation-cap', 'color': '#3b82f6'},
            {'name': 'Sosial', 'category_type': 'social', 'icon': 'fas fa-users', 'color': '#06b6d4'},
            {'name': 'Əyləncə', 'category_type': 'entertainment', 'icon': 'fas fa-gamepad', 'color': '#a855f7'},
            {'name': 'Musiqi', 'category_type': 'music', 'icon': 'fas fa-music', 'color': '#10b981'},
            {'name': 'Fotoqrafiya', 'category_type': 'photography', 'icon': 'fas fa-camera', 'color': '#6366f1'},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = ActivityCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['category_type']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Sample activities data
        base_date = timezone.now() + timedelta(days=1)
        activities_data = [
            {
                'title': 'Şahdağ Milli Parkı Gəzintisi',
                'category': 'nature',
                'short_description': 'Təbiətin qoynunda gözəl gün keçirmək və yeni dostlar tapmaq üçün',
                'description': 'Şahdağ Milli Parkında təşkil olunan bu gəzinti təbiət sevərləri üçün ideal imkandır. Gəzinti zamanı gözəl mənzərələr, təmiz hava və yeni dostluqlar sizi gözləyir.',
                'location_name': 'Şahdağ Milli Parkı',
                'address': 'Quba-Qusar yolu, Şahdağ',
                'district': 'other',
                'max_participants': 12,
                'min_participants': 4,
                'duration_hours': 8,
                'difficulty_level': 'intermediate',
                'is_free': False,
                'price': 25.00,
                'is_featured': True,
                'start_date': base_date + timedelta(days=1, hours=8),
                'end_date': base_date + timedelta(days=1, hours=16),
                'requirements': 'Rahat geyim, idman ayaqqabısı, su və yemək',
                'what_included': 'Nəqliyyat, bələdçi xidməti, ilk yardım dəsti',
                'contact_phone': '+994 50 123 45 67'
            },
            {
                'title': 'Milli Mətbəx Festivalı',
                'category': 'food',
                'short_description': 'Azərbaycan mətbəxinin ləzzətlərini dadmaq və öyrənmək',
                'description': 'Bakı Bulvarında keçiriləcək bu festival zamanı Azərbaycan mətbəxinin ən dadlı yeməklərini dadacaq və hazırlanma sirlərini öyrənəcəksiniz.',
                'location_name': 'Bakı Bulvarı',
                'address': 'Dənizkənarı Milli Park, Bakı Bulvarı',
                'district': 'sabail',
                'max_participants': 20,
                'min_participants': 5,
                'duration_hours': 4,
                'difficulty_level': 'beginner',
                'is_free': False,
                'price': 15.00,
                'is_featured': True,
                'start_date': base_date + timedelta(days=3, hours=14),
                'end_date': base_date + timedelta(days=3, hours=18),
                'requirements': 'Heç nə lazım deyil',
                'what_included': 'Bütün yeməklər, içkilər və reseptlər',
                'contact_phone': '+994 50 234 56 78'
            },
            {
                'title': 'İçəri Şəhər Fotoqrafiya Turu',
                'category': 'photography',
                'short_description': 'Tarixi İçəri Şəhərin gözəl küncələrini fotoqraflamaq',
                'description': 'Professional fotoqrafçı ilə birlikdə tarixi İçəri Şəhərin ən gözəl yerlərini kəşf edəcək və fotoqrafiya bacarığınızı inkişaf etdirəcəksiniz.',
                'location_name': 'İçəri Şəhər',
                'address': 'Şirvanşahlar Sarayı, İçəri Şəhər',
                'district': 'sabail',
                'max_participants': 10,
                'min_participants': 3,
                'duration_hours': 3,
                'difficulty_level': 'intermediate',
                'is_free': False,
                'price': 20.00,
                'is_featured': False,
                'start_date': base_date + timedelta(days=5, hours=10),
                'end_date': base_date + timedelta(days=5, hours=13),
                'requirements': 'Fotoqraf (telefon da olar), rahat ayaqqabı',
                'what_included': 'Professional bələdçi, fotoqrafiya məsləhətləri',
                'contact_phone': '+994 50 345 67 89'
            },
            {
                'title': 'Səhər Yoga Seansı',
                'category': 'sports',
                'short_description': 'Gün ərzində enerjili olmaq üçün səhər yoga məşğələsi',
                'description': 'Dənizkənarı Parkda təşkil olunan səhər yoga seansı ilə gününüzə enerjili başlayın. Təcrübəli instruktor rəhbərliyində yoga hərekatları öyrənəcəksiniz.',
                'location_name': 'Dənizkənarı Park',
                'address': 'Dənizkənarı Milli Park',
                'district': 'sabail',
                'max_participants': 15,
                'min_participants': 5,
                'duration_hours': 1,
                'difficulty_level': 'beginner',
                'is_free': True,
                'price': 0.00,
                'is_featured': True,
                'start_date': base_date + timedelta(days=2, hours=7),
                'end_date': base_date + timedelta(days=2, hours=8),
                'requirements': 'Yoga matı, rahat geyim',
                'what_included': 'Yoga matı (lazım olsa), su',
                'contact_phone': '+994 50 456 78 90'
            },
            {
                'title': 'Kitab Klubu Görüşü',
                'category': 'education',
                'short_description': 'Oxuduğumuz kitabları müzakirə edib yeni dostlar tapırıq',
                'description': 'Bu ay "Arşın mal alan" əsərini oxuduq və indi birlikdə müzakirə edəcəyik. Kitab sevərlər üçün ideal imkan.',
                'location_name': 'Mərkəzi Kitabxana',
                'address': 'M.F.Axundov adına Azərbaycan Milli Kitabxanası',
                'district': 'sabail',
                'max_participants': 12,
                'min_participants': 4,
                'duration_hours': 2,
                'difficulty_level': 'beginner',
                'is_free': True,
                'price': 0.00,
                'is_featured': False,
                'start_date': base_date + timedelta(days=7, hours=18),
                'end_date': base_date + timedelta(days=7, hours=20),
                'requirements': 'Kitabı oxumuş olmaq',
                'what_included': 'Çay, şirniyyat',
                'contact_phone': '+994 50 567 89 01'
            },
            {
                'title': 'Jazz Konsert Gecəsi',
                'category': 'music',
                'short_description': 'Canlı jazz musiqisi dinləyərək keyfiyyətli vaxt keçirmək',
                'description': 'Bakının məşhur jazz klubunda keçiriləcək bu gecədə yerli və beynəlxalq jazz musiqiçilərinin möhtəşəm çıxışları olacaq.',
                'location_name': 'Baku Jazz Club',
                'address': 'Fountain Square, Jazz Club',
                'district': 'sabail',
                'max_participants': 20,
                'min_participants': 8,
                'duration_hours': 3,
                'difficulty_level': 'beginner',
                'is_free': False,
                'price': 30.00,
                'is_featured': True,
                'start_date': base_date + timedelta(days=10, hours=20),
                'end_date': base_date + timedelta(days=10, hours=23),
                'requirements': 'Heç nə',
                'what_included': 'Canlı musiqi, bir içki',
                'contact_phone': '+994 50 678 90 12'
            },
            {
                'title': 'Bowling Gecəsi',
                'category': 'entertainment',
                'short_description': 'Dostlarla əyləncəli bowling oyunu',
                'description': 'Həftə sonu dostlarla birlikdə bowling oynayaraq əyləncəli vaxt keçirin. Hər səviyyədən iştirakçı qəbul olunur.',
                'location_name': 'Bowling City',
                'address': 'Gənclik Mall, Babək prospekti',
                'district': 'binagadi',
                'max_participants': 16,
                'min_participants': 6,
                'duration_hours': 2,
                'difficulty_level': 'beginner',
                'is_free': False,
                'price': 12.00,
                'is_featured': False,
                'start_date': base_date + timedelta(days=6, hours=19),
                'end_date': base_date + timedelta(days=6, hours=21),
                'requirements': 'Rahat geyim',
                'what_included': 'Bowling oyunu, ayaqqabı kirayəsi',
                'contact_phone': '+994 50 789 01 23'
            },
            {
                'title': 'İncəsənət Atölyəsi',
                'category': 'art',
                'short_description': 'Rəsm və əl işlərini öyrənmək üçün yaradıcı atölye',
                'description': 'Yaradıcı atölyədə rəsm çəkməyi və müxtəlif əl işlərini öyrənəcək, öz sənət əsərinizi yaradacaqsınız.',
                'location_name': 'Sənət Mərkəzi',
                'address': 'Yasamal rayonu, Sənət Mərkəzi',
                'district': 'yasamal',
                'max_participants': 10,
                'min_participants': 5,
                'duration_hours': 3,
                'difficulty_level': 'beginner',
                'is_free': False,
                'price': 18.00,
                'is_featured': False,
                'start_date': base_date + timedelta(days=8, hours=15),
                'end_date': base_date + timedelta(days=8, hours=18),
                'requirements': 'Heç nə',
                'what_included': 'Bütün materiallar, çay',
                'contact_phone': '+994 50 890 12 34'
            }
        ]

        for activity_data in activities_data:
            category = categories[activity_data.pop('category')]
            activity_data['category'] = category
            activity_data['organizer'] = organizer
            activity_data['status'] = 'published'
            
            activity, created = Activity.objects.get_or_create(
                title=activity_data['title'],
                defaults=activity_data
            )
            if created:
                self.stdout.write(f'Created activity: {activity.title}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created sample data with {len(categories_data)} categories and {len(activities_data)} activities!')
        )

from django.utils import timezone
from activities.models import ActivityCategory, Activity
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample activities data for demonstration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample activities data...'))

        # Get or create a superuser as organizer
        try:
            organizer = User.objects.filter(is_superuser=True).first()
            if not organizer:
                organizer = User.objects.create_superuser(
                    phone='+994501234567',
                    first_name='Acteezer',
                    last_name='Admin',
                    email='admin@acteezer.az',
                    password='admin123'
                )
                self.stdout.write(f'Created organizer: {organizer.get_full_name()}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating organizer: {e}'))
            return

        # Create categories
        categories_data = [
            {'name': 'İdman', 'category_type': 'sports', 'icon': 'fas fa-running', 'color': '#ef4444'},
            {'name': 'Mədəniyyət', 'category_type': 'culture', 'icon': 'fas fa-theater-masks', 'color': '#8b5cf6'},
            {'name': 'Təbiət', 'category_type': 'nature', 'icon': 'fas fa-tree', 'color': '#22c55e'},
            {'name': 'Sənət', 'category_type': 'art', 'icon': 'fas fa-palette', 'color': '#f59e0b'},
            {'name': 'Yemək', 'category_type': 'food', 'icon': 'fas fa-utensils', 'color': '#ec4899'},
            {'name': 'Təhsil', 'category_type': 'education', 'icon': 'fas fa-graduation-cap', 'color': '#3b82f6'},
            {'name': 'Sosial', 'category_type': 'social', 'icon': 'fas fa-users', 'color': '#06b6d4'},
            {'name': 'Əyləncə', 'category_type': 'entertainment', 'icon': 'fas fa-gamepad', 'color': '#a855f7'},
            {'name': 'Musiqi', 'category_type': 'music', 'icon': 'fas fa-music', 'color': '#10b981'},
            {'name': 'Fotoqrafiya', 'category_type': 'photography', 'icon': 'fas fa-camera', 'color': '#6366f1'},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = ActivityCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['category_type']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Sample activities data
        base_date = timezone.now() + timedelta(days=1)
        activities_data = [
            {
                'title': 'Şahdağ Milli Parkı Gəzintisi',
                'category': 'nature',
                'short_description': 'Təbiətin qoynunda gözəl gün keçirmək və yeni dostlar tapmaq üçün',
                'description': 'Şahdağ Milli Parkında təşkil olunan bu gəzinti təbiət sevərləri üçün ideal imkandır. Gəzinti zamanı gözəl mənzərələr, təmiz hava və yeni dostluqlar sizi gözləyir.',
                'location_name': 'Şahdağ Milli Parkı',
                'address': 'Quba-Qusar yolu, Şahdağ',
                'district': 'other',
                'max_participants': 12,
                'min_participants': 4,
                'duration_hours': 8,
                'difficulty_level': 'intermediate',
                'is_free': False,
                'price': 25.00,
                'is_featured': True,
                'start_date': base_date + timedelta(days=1, hours=8),
                'end_date': base_date + timedelta(days=1, hours=16),
                'requirements': 'Rahat geyim, idman ayaqqabısı, su və yemək',
                'what_included': 'Nəqliyyat, bələdçi xidməti, ilk yardım dəsti',
                'contact_phone': '+994 50 123 45 67'
            },
            {
                'title': 'Milli Mətbəx Festivalı',
                'category': 'food',
                'short_description': 'Azərbaycan mətbəxinin ləzzətlərini dadmaq və öyrənmək',
                'description': 'Bakı Bulvarında keçiriləcək bu festival zamanı Azərbaycan mətbəxinin ən dadlı yeməklərini dadacaq və hazırlanma sirlərini öyrənəcəksiniz.',
                'location_name': 'Bakı Bulvarı',
                'address': 'Dənizkənarı Milli Park, Bakı Bulvarı',
                'district': 'sabail',
                'max_participants': 20,
                'min_participants': 5,
                'duration_hours': 4,
                'difficulty_level': 'beginner',
                'is_free': False,
                'price': 15.00,
                'is_featured': True,
                'start_date': base_date + timedelta(days=3, hours=14),
                'end_date': base_date + timedelta(days=3, hours=18),
                'requirements': 'Heç nə lazım deyil',
                'what_included': 'Bütün yeməklər, içkilər və reseptlər',
                'contact_phone': '+994 50 234 56 78'
            },
            {
                'title': 'İçəri Şəhər Fotoqrafiya Turu',
                'category': 'photography',
                'short_description': 'Tarixi İçəri Şəhərin gözəl küncələrini fotoqraflamaq',
                'description': 'Professional fotoqrafçı ilə birlikdə tarixi İçəri Şəhərin ən gözəl yerlərini kəşf edəcək və fotoqrafiya bacarığınızı inkişaf etdirəcəksiniz.',
                'location_name': 'İçəri Şəhər',
                'address': 'Şirvanşahlar Sarayı, İçəri Şəhər',
                'district': 'sabail',
                'max_participants': 10,
                'min_participants': 3,
                'duration_hours': 3,
                'difficulty_level': 'intermediate',
                'is_free': False,
                'price': 20.00,
                'is_featured': False,
                'start_date': base_date + timedelta(days=5, hours=10),
                'end_date': base_date + timedelta(days=5, hours=13),
                'requirements': 'Fotoqraf (telefon da olar), rahat ayaqqabı',
                'what_included': 'Professional bələdçi, fotoqrafiya məsləhətləri',
                'contact_phone': '+994 50 345 67 89'
            },
            {
                'title': 'Səhər Yoga Seansı',
                'category': 'sports',
                'short_description': 'Gün ərzində enerjili olmaq üçün səhər yoga məşğələsi',
                'description': 'Dənizkənarı Parkda təşkil olunan səhər yoga seansı ilə gününüzə enerjili başlayın. Təcrübəli instruktor rəhbərliyində yoga hərekatları öyrənəcəksiniz.',
                'location_name': 'Dənizkənarı Park',
                'address': 'Dənizkənarı Milli Park',
                'district': 'sabail',
                'max_participants': 15,
                'min_participants': 5,
                'duration_hours': 1,
                'difficulty_level': 'beginner',
                'is_free': True,
                'price': 0.00,
                'is_featured': True,
                'start_date': base_date + timedelta(days=2, hours=7),
                'end_date': base_date + timedelta(days=2, hours=8),
                'requirements': 'Yoga matı, rahat geyim',
                'what_included': 'Yoga matı (lazım olsa), su',
                'contact_phone': '+994 50 456 78 90'
            },
            {
                'title': 'Kitab Klubu Görüşü',
                'category': 'education',
                'short_description': 'Oxuduğumuz kitabları müzakirə edib yeni dostlar tapırıq',
                'description': 'Bu ay "Arşın mal alan" əsərini oxuduq və indi birlikdə müzakirə edəcəyik. Kitab sevərlər üçün ideal imkan.',
                'location_name': 'Mərkəzi Kitabxana',
                'address': 'M.F.Axundov adına Azərbaycan Milli Kitabxanası',
                'district': 'sabail',
                'max_participants': 12,
                'min_participants': 4,
                'duration_hours': 2,
                'difficulty_level': 'beginner',
                'is_free': True,
                'price': 0.00,
                'is_featured': False,
                'start_date': base_date + timedelta(days=7, hours=18),
                'end_date': base_date + timedelta(days=7, hours=20),
                'requirements': 'Kitabı oxumuş olmaq',
                'what_included': 'Çay, şirniyyat',
                'contact_phone': '+994 50 567 89 01'
            },
            {
                'title': 'Jazz Konsert Gecəsi',
                'category': 'music',
                'short_description': 'Canlı jazz musiqisi dinləyərək keyfiyyətli vaxt keçirmək',
                'description': 'Bakının məşhur jazz klubunda keçiriləcək bu gecədə yerli və beynəlxalq jazz musiqiçilərinin möhtəşəm çıxışları olacaq.',
                'location_name': 'Baku Jazz Club',
                'address': 'Fountain Square, Jazz Club',
                'district': 'sabail',
                'max_participants': 20,
                'min_participants': 8,
                'duration_hours': 3,
                'difficulty_level': 'beginner',
                'is_free': False,
                'price': 30.00,
                'is_featured': True,
                'start_date': base_date + timedelta(days=10, hours=20),
                'end_date': base_date + timedelta(days=10, hours=23),
                'requirements': 'Heç nə',
                'what_included': 'Canlı musiqi, bir içki',
                'contact_phone': '+994 50 678 90 12'
            },
            {
                'title': 'Bowling Gecəsi',
                'category': 'entertainment',
                'short_description': 'Dostlarla əyləncəli bowling oyunu',
                'description': 'Həftə sonu dostlarla birlikdə bowling oynayaraq əyləncəli vaxt keçirin. Hər səviyyədən iştirakçı qəbul olunur.',
                'location_name': 'Bowling City',
                'address': 'Gənclik Mall, Babək prospekti',
                'district': 'binagadi',
                'max_participants': 16,
                'min_participants': 6,
                'duration_hours': 2,
                'difficulty_level': 'beginner',
                'is_free': False,
                'price': 12.00,
                'is_featured': False,
                'start_date': base_date + timedelta(days=6, hours=19),
                'end_date': base_date + timedelta(days=6, hours=21),
                'requirements': 'Rahat geyim',
                'what_included': 'Bowling oyunu, ayaqqabı kirayəsi',
                'contact_phone': '+994 50 789 01 23'
            },
            {
                'title': 'İncəsənət Atölyəsi',
                'category': 'art',
                'short_description': 'Rəsm və əl işlərini öyrənmək üçün yaradıcı atölye',
                'description': 'Yaradıcı atölyədə rəsm çəkməyi və müxtəlif əl işlərini öyrənəcək, öz sənət əsərinizi yaradacaqsınız.',
                'location_name': 'Sənət Mərkəzi',
                'address': 'Yasamal rayonu, Sənət Mərkəzi',
                'district': 'yasamal',
                'max_participants': 10,
                'min_participants': 5,
                'duration_hours': 3,
                'difficulty_level': 'beginner',
                'is_free': False,
                'price': 18.00,
                'is_featured': False,
                'start_date': base_date + timedelta(days=8, hours=15),
                'end_date': base_date + timedelta(days=8, hours=18),
                'requirements': 'Heç nə',
                'what_included': 'Bütün materiallar, çay',
                'contact_phone': '+994 50 890 12 34'
            }
        ]

        for activity_data in activities_data:
            category = categories[activity_data.pop('category')]
            activity_data['category'] = category
            activity_data['organizer'] = organizer
            activity_data['status'] = 'published'
            
            activity, created = Activity.objects.get_or_create(
                title=activity_data['title'],
                defaults=activity_data
            )
            if created:
                self.stdout.write(f'Created activity: {activity.title}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created sample data with {len(categories_data)} categories and {len(activities_data)} activities!')
        )
