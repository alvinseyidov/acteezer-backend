from django.core.management.base import BaseCommand
from accounts.models import Language, Interest


class Command(BaseCommand):
    help = 'Set up initial data for languages and interests'

    def handle(self, *args, **options):
        self.stdout.write('Setting up initial data...')
        
        # Create Languages
        languages_data = [
            ('Azərbaycan dili', 'az'),
            ('English', 'en'),
            ('Русский', 'ru'),
            ('Türkçe', 'tr'),
            ('فارسی', 'fa'),
            ('العربية', 'ar'),
            ('Español', 'es'),
            ('Français', 'fr'),
            ('Deutsch', 'de'),
            ('Italiano', 'it'),
            ('Português', 'pt'),
            ('中文', 'zh'),
            ('日本語', 'ja'),
            ('한국어', 'ko'),
            ('हिंदी', 'hi'),
            ('Nederlands', 'nl'),
            ('Svenska', 'sv'),
            ('Norsk', 'no'),
            ('Dansk', 'da'),
            ('Suomi', 'fi'),
            ('Polski', 'pl'),
            ('Čeština', 'cs'),
            ('Magyar', 'hu'),
            ('Română', 'ro'),
            ('Български', 'bg'),
            ('Hrvatski', 'hr'),
            ('Српски', 'sr'),
            ('Slovenčina', 'sk'),
            ('Slovenščina', 'sl'),
            ('Ελληνικά', 'el'),
            ('עברית', 'he'),
            ('Türkmen', 'tk'),
            ('Қазақ', 'kk'),
            ('Oʻzbek', 'uz'),
            ('ქართული', 'ka'),
            ('Հայերեն', 'hy'),
            ('Македонски', 'mk'),
            ('Lietuvių', 'lt'),
            ('Latviešu', 'lv'),
            ('Eesti', 'et'),
            ('Íslenska', 'is'),
            ('Gaeilge', 'ga'),
            ('Català', 'ca'),
            ('Galego', 'gl'),
            ('Беларуская', 'be'),
            ('Українська', 'uk'),
            ('Tiếng Việt', 'vi'),
            ('ไทย', 'th'),
            ('Bahasa Indonesia', 'id'),
            ('Bahasa Melayu', 'ms'),
            ('Tagalog', 'tl'),
            ('Kiswahili', 'sw'),
            ('Afrikaans', 'af'),
            ('Zulu', 'zu'),
            ('Xhosa', 'xh'),
        ]
        
        for name, code in languages_data:
            language, created = Language.objects.get_or_create(
                code=code,
                defaults={'name': name}
            )
            if created:
                self.stdout.write(f'Created language: {name}')
        
        # Create Interests
        # Format: (name, icon, category, is_general)
        interests_data = [
            # General/Popular - These will show first
            ('Səyahət', 'plane', 'travel', True),
            ('Musiqi', 'music', 'music', True),
            ('Fotoqrafiya', 'camera', 'arts', True),
            ('Yemək bişirmə', 'utensils', 'food', True),
            ('Oxumaq', 'book', 'education', True),
            ('İdman', 'football-ball', 'sports', True),
            ('Sənət', 'palette', 'arts', True),
            ('Yoga', 'leaf', 'health', True),
            ('Təbiət', 'tree', 'nature', True),
            ('Gözəllik', 'spa', 'beauty', True),
            ('Ev heyvanları', 'paw', 'lifestyle', True),
            
            # Beauty & Fashion - Related to general beauty/pets
            ('Makiyaj', 'palette', 'beauty', False),
            ('Saç baxımı və stil', 'cut', 'beauty', False),
            ('Dəri baxımı', 'spa', 'beauty', False),
            ('Qadın geyimləri', 'tshirt', 'beauty', False),
            ('Kişi geyimləri', 'tshirt', 'beauty', False),
            ('Aksesuarlar', 'gem', 'beauty', False),
            ('Parfüm', 'spray-can', 'beauty', False),
            ('Dırnaq dizaynı', 'hand-paper', 'beauty', False),
            
            # Lifestyle & Home - Related to pets/interior design
            ('İnteryer dizayn', 'couch', 'lifestyle', False),
            ('Ev dekorasiyası', 'home', 'lifestyle', False),
            ('Partiya planlaşdırma', 'birthday-cake', 'lifestyle', False),
            ('Uşaqlar və körpələr', 'baby', 'lifestyle', False),
            ('Bağçılıq', 'seedling', 'lifestyle', False),
            ('Otaq əşyaları', 'couch', 'lifestyle', False),
            ('Təmizlik', 'broom', 'lifestyle', False),
            ('Təşkilatçılıq', 'tasks', 'lifestyle', False),
            ('Minimalizm', 'home', 'lifestyle', False),
            
            # Pets - More specific
            ('İtlər', 'paw', 'lifestyle', False),
            ('Pişiklər', 'paw', 'lifestyle', False),
            ('Balıqlar', 'fish', 'lifestyle', False),
            ('Quşlar', 'dove', 'lifestyle', False),
            ('Kənd təsərrüfatı heyvanları', 'paw', 'lifestyle', False),
            
            # Sports & Fitness
            ('Futbol', 'football-ball', 'sports', False),
            ('Basketbol', 'basketball-ball', 'sports', False),
            ('Tennis', 'table-tennis', 'sports', False),
            ('Üzmək', 'swimmer', 'sports', False),
            ('Qaçış', 'running', 'sports', False),
            ('Velosiped', 'bicycle', 'sports', False),
            ('Dağçılıq', 'mountain', 'sports', False),
            ('Dırmaşma', 'mountain', 'sports', False),
            ('Qış idmanı', 'skiing', 'sports', False),
            ('Sörf', 'water', 'sports', False),
            ('Fitness', 'dumbbell', 'sports', False),
            ('Çimərlik voleybolu', 'volleyball-ball', 'sports', False),
            ('Boks', 'fist-raised', 'sports', False),
            ('Yürüş', 'walking', 'sports', False),
            
            # Arts & Culture
            ('Rəsm', 'paint-brush', 'arts', False),
            ('Kinolar', 'film', 'arts', False),
            ('Teatr', 'theater-masks', 'arts', False),
            ('Rəqs', 'music', 'arts', False),
            ('Yazıçılıq', 'pen', 'arts', False),
            ('Hekayə danışma', 'microphone', 'arts', False),
            ('Heykəltəraşlıq', 'monument', 'arts', False),
            ('Muzeylər', 'university', 'arts', False),
            ('Qalereya', 'images', 'arts', False),
            ('Sənət tarixi', 'landmark', 'arts', False),
            
            # Food & Dining
            ('Şərab dadmaq', 'wine-glass', 'food', False),
            ('Qəhvə', 'coffee', 'food', False),
            ('Çay', 'coffee', 'food', False),
            ('Restoranlar', 'hamburger', 'food', False),
            ('Piknik', 'utensils', 'food', False),
            ('Pəhriz və sağlamlıq', 'apple-alt', 'food', False),
            ('Vegan yemək', 'leaf', 'food', False),
            ('Desertlər', 'birthday-cake', 'food', False),
            ('Barbekü', 'fire', 'food', False),
            
            # Travel & Adventure
            ('Düşərgə', 'campground', 'travel', False),
            ('Backpacking', 'backpack', 'travel', False),
            ('Tarixi yerlər', 'landmark', 'travel', False),
            ('Mədəniyyət turizmi', 'monument', 'travel', False),
            ('Macəra turizmi', 'mountain', 'travel', False),
            ('Plaj gəzintiləri', 'umbrella-beach', 'travel', False),
            ('Şəhər gəzintiləri', 'city', 'travel', False),
            ('Ekoturizm', 'tree', 'travel', False),
            
            # Technology
            ('Texnologiya', 'laptop', 'tech', False),
            ('Proqramlaşdırma', 'code', 'tech', False),
            ('Video oyunlar', 'gamepad', 'tech', False),
            ('Masa oyunları', 'chess', 'tech', False),
            ('Robotika', 'robot', 'tech', False),
            ('AI və Maşın öyrənmə', 'brain', 'tech', False),
            ('VR/AR', 'vr-cardboard', 'tech', False),
            ('Kriptovalyuta', 'coins', 'tech', False),
            ('Blockchain', 'link', 'tech', False),
            
            # Music
            ('Gitara', 'guitar', 'music', False),
            ('Piano', 'music', 'music', False),
            ('Vokal', 'microphone', 'music', False),
            ('Konsertlər', 'music', 'music', False),
            ('Festivallar', 'music', 'music', False),
            ('DJ', 'headphones', 'music', False),
            ('Prodüserlik', 'microphone-alt', 'music', False),
            ('Musiqi baxışı', 'music', 'music', False),
            
            # Nature & Outdoors
            ('Heyvanlar', 'paw', 'nature', False),
            ('Quş müşahidəsi', 'dove', 'nature', False),
            ('Balıq tutmaq', 'fish', 'nature', False),
            ('Açıq hava macəraları', 'tree', 'nature', False),
            ('Gəzinti', 'hiking', 'nature', False),
            ('Geologiya', 'mountain', 'nature', False),
            ('Astronomiya', 'moon', 'nature', False),
            ('Bitki yetişdirmə', 'seedling', 'nature', False),
            
            # Additional Lifestyle interests
            ('Gənclər', 'user-friends', 'lifestyle', False),
            ('Dorm əsasları', 'home', 'lifestyle', False),
            ('Məktəb ləvazimatları', 'school', 'lifestyle', False),
            
            # Education & Learning
            ('Dil öyrənmək', 'language', 'education', False),
            ('Tarix', 'landmark', 'education', False),
            ('Elm', 'flask', 'education', False),
            ('Fəlsəfə', 'book', 'education', False),
            ('Psixologiya', 'brain', 'education', False),
            ('Maliyyə', 'dollar-sign', 'education', False),
            ('Məşq etmək', 'chalkboard-teacher', 'education', False),
            ('Online kurslar', 'laptop', 'education', False),
            ('Kitab klubları', 'book-reader', 'education', False),
            
            # Health & Wellness
            ('Sağlamlıq', 'heartbeat', 'health', False),
            ('Meditasiya', 'peace', 'health', False),
            ('Pilates', 'dumbbell', 'health', False),
            ('Sağlam qidalanma', 'apple-alt', 'health', False),
            ('Uyğunluq', 'dumbbell', 'health', False),
            ('Mental sağlamlıq', 'brain', 'health', False),
            ('Masaj', 'spa', 'health', False),
            ('Aromaterapiya', 'spray-can', 'health', False),
            
            # Social & Volunteering
            ('Könüllülük', 'hands-helping', 'social', False),
            ('Xeyriyyə', 'heart', 'social', False),
            ('İctimai işlər', 'users', 'social', False),
            ('Networking', 'network-wired', 'social', False),
            ('Gecə həyatı', 'cocktail', 'social', False),
            ('Pub', 'beer', 'social', False),
            ('Bar', 'wine-glass', 'social', False),
            ('Klub', 'headphones', 'social', False),
        ]
        
        # English to Azerbaijani mapping for updating old interests
        english_to_azeri = {
            'Animals': 'Heyvanlar',
            'Art': 'Sənət',
            'Backpacking': 'Backpacking',
            'Bar': 'Bar',
            'Beauty': 'Gözəllik',
            'Blockchain': 'Blockchain',
            'Camping': 'Düşərgə',
            'Climbing': 'Dırmaşma',
            'Club': 'Klub',
            'Coffee': 'Qəhvə',
            'Concert': 'Konsertlər',
            'Cooking': 'Yemək bişirmə',
            'Cryptocurrency': 'Kriptovalyuta',
            'Dancing': 'Rəqs',
            'Dining': 'Restoranlar',
            'DJ': 'DJ',
            'Dogs': 'İtlər',
            'Education': 'Təhsil',
            'Fashion': 'Moda',
            'Festival': 'Festivallar',
            'Fitness': 'Fitness',
            'Food': 'Yemək bişirmə',
            'Football': 'Futbol',
            'Gardening': 'Bağçılıq',
            'Guitar': 'Gitara',
            'Gaming': 'Video oyunlar',
            'Hiking': 'Gəzinti',
            'Interior Design': 'İnteryer dizayn',
            'Literature': 'Yazıçılıq',
            'Makeup': 'Makiyaj',
            'Martial Arts': 'Boks',
            'Meditation': 'Meditasiya',
            'Movies': 'Kinolar',
            'Music': 'Musiqi',
            'Nature': 'Təbiət',
            'Party Planning': 'Partiya planlaşdırma',
            'Pets': 'Ev heyvanları',
            'Photography': 'Fotoqrafiya',
            'Piano': 'Piano',
            'Pub': 'Pub',
            'Reading': 'Oxumaq',
            'Robotics': 'Robotika',
            'Running': 'Qaçış',
            'Skin Care': 'Dəri baxımı',
            'Skiing': 'Qış idmanı',
            'Sports': 'İdman',
            'Surfing': 'Sörf',
            'Swimming': 'Üzmək',
            'Technology': 'Texnologiya',
            'Theater': 'Teatr',
            'Travel': 'Səyahət',
            'Volunteering': 'Könüllülük',
            'Wine Tasting': 'Şərab dadmaq',
            'Writing': 'Yazıçılıq',
            'Yoga': 'Yoga',
        }
        
        # First, update any existing English interests to Azerbaijani
        updated_count = 0
        deleted_count = 0
        for eng_name, azeri_name in english_to_azeri.items():
            try:
                old_interest = Interest.objects.get(name=eng_name)
                # Check if Azerbaijani version already exists
                if not Interest.objects.filter(name=azeri_name).exists():
                    old_interest.name = azeri_name
                    old_interest.save()
                    updated_count += 1
                else:
                    # If Azerbaijani version exists, delete the English one
                    old_interest.delete()
                    deleted_count += 1
            except Interest.DoesNotExist:
                pass
        
        if updated_count > 0 or deleted_count > 0:
            self.stdout.write(f'Updated {updated_count} interests, deleted {deleted_count} duplicates')
        
        # Now create/update all interests
        created_count = 0
        updated_count = 0
        for item in interests_data:
            if len(item) == 4:
                name, icon, category, is_general = item
            else:
                # Handle old format for backward compatibility
                name, icon = item
                category = 'general'
                is_general = False
            
            interest, created = Interest.objects.get_or_create(
                name=name,
                defaults={
                    'icon': icon,
                    'category': category,
                    'is_general': is_general
                }
            )
            if not created:
                # Update existing interests
                interest.icon = icon
                interest.category = category
                interest.is_general = is_general
                interest.save()
                updated_count += 1
            else:
                created_count += 1
        
        self.stdout.write(f'Created {created_count} interests, updated {updated_count} interests')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up initial data!')
        )
