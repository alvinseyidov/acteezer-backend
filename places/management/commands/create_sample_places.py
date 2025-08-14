from django.core.management.base import BaseCommand
from places.models import PlaceCategory, Place
import random


class Command(BaseCommand):
    help = 'Create sample places data for demonstration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample places data...'))

        # Create categories
        categories_data = [
            {'name': 'Restoranlar', 'category_type': 'restaurant', 'icon': 'fas fa-utensils', 'color': '#ff6b6b'},
            {'name': 'Publar', 'category_type': 'pub', 'icon': 'fas fa-beer', 'color': '#ffa726'},
            {'name': 'Klublar', 'category_type': 'club', 'icon': 'fas fa-music', 'color': '#ab47bc'},
            {'name': 'Kafelər', 'category_type': 'cafe', 'icon': 'fas fa-coffee', 'color': '#8d6e63'},
            {'name': 'Barlar', 'category_type': 'bar', 'icon': 'fas fa-cocktail', 'color': '#26a69a'},
            {'name': 'Aktivlik Məkanları', 'category_type': 'activity', 'icon': 'fas fa-gamepad', 'color': '#42a5f5'},
            {'name': 'Muzeylər', 'category_type': 'museum', 'icon': 'fas fa-landmark', 'color': '#78909c'},
            {'name': 'Parklar', 'category_type': 'park', 'icon': 'fas fa-tree', 'color': '#66bb6a'},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = PlaceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['category_type']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Sample places data
        places_data = [
            {
                'name': 'Firuze Restaurant',
                'category': 'restaurant',
                'short_description': 'Azərbaycan mətbəxinin ən dadlı yeməkləri və müasir atmosfer',
                'description': 'Firuze Restaurant Bakının mərkəzində yerləşən və milli mətbəxin ən yaxşı nümunələrini təqdim edən prestijli restoranlardandır.',
                'address': 'Nizami küçəsi 89, Bakı',
                'district': 'nizami',
                'phone': '+994 12 493 12 34',
                'price_range': 'expensive',
                'rating': 4.7,
                'review_count': 245,
                'is_featured': True,
                'is_verified': True,
                'opening_hours': 'Hər gün 12:00-24:00',
                'features': 'Təmiz hava, Ailə dostu, Rezervasiya məcburi'
            },
            {
                'name': 'Baku Jazz Club',
                'category': 'club',
                'short_description': 'Canlı jazz musiqisi və Premium kokteyllər',
                'description': 'Bakıda jazz musiqisinin ürək məkanı olan klub, canlı ifalar və əla musiqi seçimi ilə.',
                'address': 'Fountain Square 12, Bakı',
                'district': 'sabail',
                'phone': '+994 12 497 45 67',
                'price_range': 'luxury',
                'rating': 4.9,
                'review_count': 189,
                'is_featured': True,
                'is_verified': True,
                'opening_hours': 'Çərşənbə axşamı-Bazar 20:00-03:00',
                'features': 'Canlı musiqi, Premium içkilər, Rezervasiya tövsiyə olunur'
            },
            {
                'name': 'Coffee Moffee',
                'category': 'cafe',
                'short_description': 'Təzə qəhvə və əla pasta seçimi',
                'description': 'Şəhərin mərkəzində rahat kafе, keyfiyyətli qəhvə və dadlı desertlərlə.',
                'address': 'Azadlıq prospekti 78, Bakı',
                'district': 'yasamal',
                'phone': '+994 12 456 78 90',
                'price_range': 'moderate',
                'rating': 4.5,
                'review_count': 156,
                'is_featured': False,
                'is_verified': True,
                'opening_hours': 'Hər gün 08:00-22:00',
                'features': 'WiFi, Laptop friendly, Vegan options'
            },
            {
                'name': 'Shark Pub',
                'category': 'pub',
                'short_description': 'Futbol matçları və geniş pivə seçimi',
                'description': 'İdman matçlarını izləmək və dostlarla vaxt keçirmək üçün ideal məkan.',
                'address': 'Həsən Əliyev küçəsi 45, Bakı',
                'district': 'narimanov',
                'phone': '+994 12 567 89 01',
                'price_range': 'budget',
                'rating': 4.2,
                'review_count': 98,
                'is_featured': False,
                'is_verified': False,
                'opening_hours': 'Hər gün 16:00-02:00',
                'features': 'İdman yayımları, Canlı oyunlar, Pivə çeşidi'
            },
            {
                'name': 'Bowling City',
                'category': 'activity',
                'short_description': 'Bowling, bilyard və əyləncə mərkəzi',
                'description': 'Ailə və dostlarla əyləncəli vaxt keçirmək üçün müasir əyləncə mərkəzi.',
                'address': 'Gənclik Mall, Babək prospekti, Bakı',
                'district': 'binagadi',
                'phone': '+994 12 345 67 89',
                'price_range': 'moderate',
                'rating': 4.4,
                'review_count': 234,
                'is_featured': True,
                'is_verified': True,
                'opening_hours': 'Hər gün 10:00-24:00',
                'features': '12 bowling zolağı, Bilyard, Uşaq oyun sahəsi'
            },
            {
                'name': 'Vino Bar',
                'category': 'bar',
                'short_description': 'Seçkin şərab və izofistos meza',
                'description': 'Şərab həvəskarları üçün premium şərab seçimi və dadlı mezələr.',
                'address': 'İçərişəhər, Bakı',
                'district': 'sabail',
                'phone': '+994 12 678 90 12',
                'price_range': 'expensive',
                'rating': 4.6,
                'review_count': 167,
                'is_featured': False,
                'is_verified': True,
                'opening_hours': 'Çərşənbə axşamı-Bazar 18:00-02:00',
                'features': 'İmportlu şərab, Romantik atmosfer, Rezervasiya məcburi'
            },
            {
                'name': 'Nizami Gəncəvi Muzeyi',
                'category': 'museum',
                'short_description': 'Azərbaycan ədəbiyyatı və tarix muzeyi',
                'description': 'Böyük şair Nizami Gəncəvinin həyatı və yaradıcılığına həsr olunmuş mədəni məkan.',
                'address': 'İstiqlaliyyət küçəsi 53, Bakı',
                'district': 'sabail',
                'phone': '+994 12 789 01 23',
                'price_range': 'budget',
                'rating': 4.3,
                'review_count': 89,
                'is_featured': False,
                'is_verified': True,
                'opening_hours': 'Bazar ertəsi-Şənbə 10:00-18:00',
                'features': 'Sərbəst giriş, Ekskursiya, Foto çəkiliş icazəsi'
            },
            {
                'name': 'Dənizkənarı Park',
                'category': 'park',
                'short_description': 'Xəzər dənizi sahilində geniş park sahəsi',
                'description': 'Bakının məşhur Dənizkənarı Parkı, gəzinti və idman üçün ideal məkan.',
                'address': 'Neftçilər prospekti, Bakı',
                'district': 'sabail',
                'phone': '',
                'price_range': 'budget',
                'rating': 4.8,
                'review_count': 456,
                'is_featured': True,
                'is_verified': True,
                'opening_hours': 'Hər gün 24 saat',
                'features': 'Açıq hava, İdman sahələri, Ailə üçün uyğun'
            },
            {
                'name': 'The Kitchen Restaurant',
                'category': 'restaurant',
                'short_description': 'Beynəlxalq mətbəx və modern dizayn',
                'description': 'Müxtəlif millətlərin yemələrini təqdim edən müasir restoran.',
                'address': 'Port Baku Mall, Bakı',
                'district': 'sabail',
                'phone': '+994 12 890 12 34',
                'price_range': 'expensive',
                'rating': 4.5,
                'review_count': 203,
                'is_featured': False,
                'is_verified': True,
                'opening_hours': 'Hər gün 11:00-23:00',
                'features': 'Beynəlxalq mətbəx, Müasir dizayn, Valet parking'
            },
            {
                'name': 'Art Garden Cafe',
                'category': 'cafe',
                'short_description': 'İncəsənət qalereya və kafе birləşməsi',
                'description': 'İncəsənət əsərlərini nümayiş etdirən və dadlı qəhvə təqdim edən unikal məkan.',
                'address': 'Fərid Əliyev küçəsi 23, Bakı',
                'district': 'khatai',
                'phone': '+994 12 234 56 78',
                'price_range': 'moderate',
                'rating': 4.7,
                'review_count': 134,
                'is_featured': True,
                'is_verified': False,
                'opening_hours': 'Hər gün 09:00-21:00',
                'features': 'Art gallery, Cozy atmosphere, Free WiFi'
            }
        ]

        for place_data in places_data:
            category = categories[place_data.pop('category')]
            place_data['category'] = category
            
            place, created = Place.objects.get_or_create(
                name=place_data['name'],
                defaults=place_data
            )
            if created:
                self.stdout.write(f'Created place: {place.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created sample data with {len(categories_data)} categories and {len(places_data)} places!')
        )

from places.models import PlaceCategory, Place
import random


class Command(BaseCommand):
    help = 'Create sample places data for demonstration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample places data...'))

        # Create categories
        categories_data = [
            {'name': 'Restoranlar', 'category_type': 'restaurant', 'icon': 'fas fa-utensils', 'color': '#ff6b6b'},
            {'name': 'Publar', 'category_type': 'pub', 'icon': 'fas fa-beer', 'color': '#ffa726'},
            {'name': 'Klublar', 'category_type': 'club', 'icon': 'fas fa-music', 'color': '#ab47bc'},
            {'name': 'Kafelər', 'category_type': 'cafe', 'icon': 'fas fa-coffee', 'color': '#8d6e63'},
            {'name': 'Barlar', 'category_type': 'bar', 'icon': 'fas fa-cocktail', 'color': '#26a69a'},
            {'name': 'Aktivlik Məkanları', 'category_type': 'activity', 'icon': 'fas fa-gamepad', 'color': '#42a5f5'},
            {'name': 'Muzeylər', 'category_type': 'museum', 'icon': 'fas fa-landmark', 'color': '#78909c'},
            {'name': 'Parklar', 'category_type': 'park', 'icon': 'fas fa-tree', 'color': '#66bb6a'},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = PlaceCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            categories[cat_data['category_type']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Sample places data
        places_data = [
            {
                'name': 'Firuze Restaurant',
                'category': 'restaurant',
                'short_description': 'Azərbaycan mətbəxinin ən dadlı yeməkləri və müasir atmosfer',
                'description': 'Firuze Restaurant Bakının mərkəzində yerləşən və milli mətbəxin ən yaxşı nümunələrini təqdim edən prestijli restoranlardandır.',
                'address': 'Nizami küçəsi 89, Bakı',
                'district': 'nizami',
                'phone': '+994 12 493 12 34',
                'price_range': 'expensive',
                'rating': 4.7,
                'review_count': 245,
                'is_featured': True,
                'is_verified': True,
                'opening_hours': 'Hər gün 12:00-24:00',
                'features': 'Təmiz hava, Ailə dostu, Rezervasiya məcburi'
            },
            {
                'name': 'Baku Jazz Club',
                'category': 'club',
                'short_description': 'Canlı jazz musiqisi və Premium kokteyllər',
                'description': 'Bakıda jazz musiqisinin ürək məkanı olan klub, canlı ifalar və əla musiqi seçimi ilə.',
                'address': 'Fountain Square 12, Bakı',
                'district': 'sabail',
                'phone': '+994 12 497 45 67',
                'price_range': 'luxury',
                'rating': 4.9,
                'review_count': 189,
                'is_featured': True,
                'is_verified': True,
                'opening_hours': 'Çərşənbə axşamı-Bazar 20:00-03:00',
                'features': 'Canlı musiqi, Premium içkilər, Rezervasiya tövsiyə olunur'
            },
            {
                'name': 'Coffee Moffee',
                'category': 'cafe',
                'short_description': 'Təzə qəhvə və əla pasta seçimi',
                'description': 'Şəhərin mərkəzində rahat kafе, keyfiyyətli qəhvə və dadlı desertlərlə.',
                'address': 'Azadlıq prospekti 78, Bakı',
                'district': 'yasamal',
                'phone': '+994 12 456 78 90',
                'price_range': 'moderate',
                'rating': 4.5,
                'review_count': 156,
                'is_featured': False,
                'is_verified': True,
                'opening_hours': 'Hər gün 08:00-22:00',
                'features': 'WiFi, Laptop friendly, Vegan options'
            },
            {
                'name': 'Shark Pub',
                'category': 'pub',
                'short_description': 'Futbol matçları və geniş pivə seçimi',
                'description': 'İdman matçlarını izləmək və dostlarla vaxt keçirmək üçün ideal məkan.',
                'address': 'Həsən Əliyev küçəsi 45, Bakı',
                'district': 'narimanov',
                'phone': '+994 12 567 89 01',
                'price_range': 'budget',
                'rating': 4.2,
                'review_count': 98,
                'is_featured': False,
                'is_verified': False,
                'opening_hours': 'Hər gün 16:00-02:00',
                'features': 'İdman yayımları, Canlı oyunlar, Pivə çeşidi'
            },
            {
                'name': 'Bowling City',
                'category': 'activity',
                'short_description': 'Bowling, bilyard və əyləncə mərkəzi',
                'description': 'Ailə və dostlarla əyləncəli vaxt keçirmək üçün müasir əyləncə mərkəzi.',
                'address': 'Gənclik Mall, Babək prospekti, Bakı',
                'district': 'binagadi',
                'phone': '+994 12 345 67 89',
                'price_range': 'moderate',
                'rating': 4.4,
                'review_count': 234,
                'is_featured': True,
                'is_verified': True,
                'opening_hours': 'Hər gün 10:00-24:00',
                'features': '12 bowling zolağı, Bilyard, Uşaq oyun sahəsi'
            },
            {
                'name': 'Vino Bar',
                'category': 'bar',
                'short_description': 'Seçkin şərab və izofistos meza',
                'description': 'Şərab həvəskarları üçün premium şərab seçimi və dadlı mezələr.',
                'address': 'İçərişəhər, Bakı',
                'district': 'sabail',
                'phone': '+994 12 678 90 12',
                'price_range': 'expensive',
                'rating': 4.6,
                'review_count': 167,
                'is_featured': False,
                'is_verified': True,
                'opening_hours': 'Çərşənbə axşamı-Bazar 18:00-02:00',
                'features': 'İmportlu şərab, Romantik atmosfer, Rezervasiya məcburi'
            },
            {
                'name': 'Nizami Gəncəvi Muzeyi',
                'category': 'museum',
                'short_description': 'Azərbaycan ədəbiyyatı və tarix muzeyi',
                'description': 'Böyük şair Nizami Gəncəvinin həyatı və yaradıcılığına həsr olunmuş mədəni məkan.',
                'address': 'İstiqlaliyyət küçəsi 53, Bakı',
                'district': 'sabail',
                'phone': '+994 12 789 01 23',
                'price_range': 'budget',
                'rating': 4.3,
                'review_count': 89,
                'is_featured': False,
                'is_verified': True,
                'opening_hours': 'Bazar ertəsi-Şənbə 10:00-18:00',
                'features': 'Sərbəst giriş, Ekskursiya, Foto çəkiliş icazəsi'
            },
            {
                'name': 'Dənizkənarı Park',
                'category': 'park',
                'short_description': 'Xəzər dənizi sahilində geniş park sahəsi',
                'description': 'Bakının məşhur Dənizkənarı Parkı, gəzinti və idman üçün ideal məkan.',
                'address': 'Neftçilər prospekti, Bakı',
                'district': 'sabail',
                'phone': '',
                'price_range': 'budget',
                'rating': 4.8,
                'review_count': 456,
                'is_featured': True,
                'is_verified': True,
                'opening_hours': 'Hər gün 24 saat',
                'features': 'Açıq hava, İdman sahələri, Ailə üçün uyğun'
            },
            {
                'name': 'The Kitchen Restaurant',
                'category': 'restaurant',
                'short_description': 'Beynəlxalq mətbəx və modern dizayn',
                'description': 'Müxtəlif millətlərin yemələrini təqdim edən müasir restoran.',
                'address': 'Port Baku Mall, Bakı',
                'district': 'sabail',
                'phone': '+994 12 890 12 34',
                'price_range': 'expensive',
                'rating': 4.5,
                'review_count': 203,
                'is_featured': False,
                'is_verified': True,
                'opening_hours': 'Hər gün 11:00-23:00',
                'features': 'Beynəlxalq mətbəx, Müasir dizayn, Valet parking'
            },
            {
                'name': 'Art Garden Cafe',
                'category': 'cafe',
                'short_description': 'İncəsənət qalereya və kafе birləşməsi',
                'description': 'İncəsənət əsərlərini nümayiş etdirən və dadlı qəhvə təqdim edən unikal məkan.',
                'address': 'Fərid Əliyev küçəsi 23, Bakı',
                'district': 'khatai',
                'phone': '+994 12 234 56 78',
                'price_range': 'moderate',
                'rating': 4.7,
                'review_count': 134,
                'is_featured': True,
                'is_verified': False,
                'opening_hours': 'Hər gün 09:00-21:00',
                'features': 'Art gallery, Cozy atmosphere, Free WiFi'
            }
        ]

        for place_data in places_data:
            category = categories[place_data.pop('category')]
            place_data['category'] = category
            
            place, created = Place.objects.get_or_create(
                name=place_data['name'],
                defaults=place_data
            )
            if created:
                self.stdout.write(f'Created place: {place.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created sample data with {len(categories_data)} categories and {len(places_data)} places!')
        )

