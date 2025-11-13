from django.core.management.base import BaseCommand
from accounts.models import Language, Interest


class Command(BaseCommand):
    help = 'Populate database with languages and interests'

    def handle(self, *args, **options):
        self.stdout.write('Starting data population...')
        
        # Populate Languages
        self.stdout.write('\nPopulating languages...')
        languages = [
            ('Azərbaycanca', 'az'),
            ('English', 'en'),
            ('Русский', 'ru'),
            ('Türkçe', 'tr'),
            ('Español', 'es'),
            ('Français', 'fr'),
            ('Deutsch', 'de'),
            ('Italiano', 'it'),
            ('Português', 'pt'),
            ('Nederlands', 'nl'),
            ('Polski', 'pl'),
            ('العربية', 'ar'),
            ('فارسی', 'fa'),
            ('中文', 'zh'),
            ('日本語', 'ja'),
            ('한국어', 'ko'),
            ('हिन्दी', 'hi'),
            ('ไทย', 'th'),
            ('Tiếng Việt', 'vi'),
            ('Bahasa Indonesia', 'id'),
            ('Українська', 'uk'),
            ('Ελληνικά', 'el'),
            ('עברית', 'he'),
            ('Svenska', 'sv'),
            ('Norsk', 'no'),
            ('Dansk', 'da'),
            ('Suomi', 'fi'),
            ('Čeština', 'cs'),
            ('Română', 'ro'),
            ('Magyar', 'hu'),
        ]
        
        for name, code in languages:
            language, created = Language.objects.get_or_create(
                code=code,
                defaults={'name': name}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created language: {name}'))
            else:
                self.stdout.write(f'Language already exists: {name}')
        
        # Populate Interests
        self.stdout.write('\nPopulating interests...')
        
        interests = [
            # General/Popular
            ('Kitab Oxumaq', 'fas fa-book', 'general', True),
            ('Film Tamaşa', 'fas fa-film', 'general', True),
            ('Musiqi', 'fas fa-music', 'general', True),
            ('Şəkil Çəkmək', 'fas fa-camera', 'general', True),
            ('Səyahət', 'fas fa-plane', 'general', True),
            ('Oyun Oynamaq', 'fas fa-gamepad', 'general', True),
            ('Alış-veriş', 'fas fa-shopping-bag', 'general', True),
            ('Yemək Hazırlamaq', 'fas fa-utensils', 'general', True),
            
            # Beauty & Fashion
            ('Makiyaj', 'fas fa-palette', 'beauty', False),
            ('Dırnaq Dizaynı', 'fas fa-hand-sparkles', 'beauty', False),
            ('Saç Baxımı', 'fas fa-cut', 'beauty', False),
            ('Cild Baxımı', 'fas fa-spa', 'beauty', False),
            ('Moda', 'fas fa-tshirt', 'beauty', False),
            ('Dəb Stil', 'fas fa-hat-cowboy', 'beauty', False),
            ('Parfüm', 'fas fa-spray-can', 'beauty', False),
            ('Zinət Əşyaları', 'fas fa-gem', 'beauty', False),
            
            # Lifestyle & Home
            ('Ev Dekorasiyası', 'fas fa-couch', 'lifestyle', False),
            ('Bağçılıq', 'fas fa-seedling', 'lifestyle', False),
            ('DIY Proyektləri', 'fas fa-hammer', 'lifestyle', False),
            ('İç Dizayn', 'fas fa-paint-roller', 'lifestyle', False),
            ('Minimalizm', 'fas fa-leaf', 'lifestyle', False),
            ('Ev Təmiri', 'fas fa-tools', 'lifestyle', False),
            ('Antik Əşyalar', 'fas fa-chess-rook', 'lifestyle', False),
            ('Qarderoб', 'fas fa-door-closed', 'lifestyle', False),
            
            # Sports & Fitness
            ('Futbol', 'fas fa-futbol', 'sports', False),
            ('Basketbol', 'fas fa-basketball-ball', 'sports', False),
            ('Tennis', 'fas fa-table-tennis', 'sports', False),
            ('Voleybol', 'fas fa-volleyball-ball', 'sports', False),
            ('İdman Zalı', 'fas fa-dumbbell', 'sports', False),
            ('Yoga', 'fas fa-spa', 'sports', False),
            ('Pilates', 'fas fa-child', 'sports', False),
            ('Qaçış', 'fas fa-running', 'sports', False),
            ('Velosiped', 'fas fa-biking', 'sports', False),
            ('Üzgüçülük', 'fas fa-swimmer', 'sports', False),
            ('Alpinizm', 'fas fa-mountain', 'sports', False),
            ('Xizək', 'fas fa-skiing', 'sports', False),
            ('Snoubord', 'fas fa-snowboarding', 'sports', False),
            ('Boks', 'fas fa-fist-raised', 'sports', False),
            ('Karate', 'fas fa-user-ninja', 'sports', False),
            ('Cüdo', 'fas fa-user-shield', 'sports', False),
            ('MMA', 'fas fa-fire', 'sports', False),
            ('Şahmat', 'fas fa-chess', 'sports', False),
            ('Bowling', 'fas fa-bowling-ball', 'sports', False),
            ('Golf', 'fas fa-golf-ball', 'sports', False),
            ('Buz Xokkeyi', 'fas fa-hockey-puck', 'sports', False),
            ('Skateboard', 'fas fa-skating', 'sports', False),
            ('Rəqs', 'fas fa-walking', 'sports', True),
            ('Tango', 'fas fa-shoe-prints', 'sports', False),
            ('Salsa', 'fas fa-fire', 'sports', False),
            ('Bachata', 'fas fa-music', 'sports', False),
            ('Vals', 'fas fa-shoe-prints', 'sports', False),
            ('Hip-Hop Rəqs', 'fas fa-music', 'sports', False),
            ('Breakdance', 'fas fa-running', 'sports', False),
            ('Müasir Rəqs', 'fas fa-walking', 'sports', False),
            ('Xalq Rəqsləri', 'fas fa-drum', 'sports', False),
            ('Flamenco', 'fas fa-fire', 'sports', False),
            ('Zumba', 'fas fa-music', 'sports', False),
            ('Bellydance', 'fas fa-spa', 'sports', False),
            
            # Arts & Culture
            ('Rəsm', 'fas fa-paint-brush', 'arts', False),
            ('Heykəltəraşlıq', 'fas fa-cube', 'arts', False),
            ('Qrafik Dizayn', 'fas fa-pencil-ruler', 'arts', False),
            ('İllüstrasiya', 'fas fa-palette', 'arts', False),
            ('Karikatura', 'fas fa-grin-squint', 'arts', False),
            ('Xət', 'fas fa-feather-alt', 'arts', False),
            ('Keramika', 'fas fa-vase', 'arts', False),
            ('Toxuculuq', 'fas fa-mitten', 'arts', False),
            ('Tikinti', 'fas fa-sewing-needle', 'arts', False),
            ('Əl İşləri', 'fas fa-hands', 'arts', False),
            ('Origami', 'fas fa-dove', 'arts', False),
            ('Teatr', 'fas fa-theater-masks', 'arts', False),
            ('Opera', 'fas fa-music', 'arts', False),
            ('Balet', 'fas fa-shoe-prints', 'arts', False),
            ('Stand-up', 'fas fa-microphone-alt', 'arts', False),
            ('Poeziya', 'fas fa-pen-fancy', 'arts', False),
            ('Yazıçılıq', 'fas fa-pen', 'arts', False),
            ('Jurnalistika', 'fas fa-newspaper', 'arts', False),
            ('Muzey', 'fas fa-landmark', 'arts', False),
            ('Arxeologiya', 'fas fa-search', 'arts', False),
            ('Tarix', 'fas fa-scroll', 'arts', False),
            
            # Food & Dining
            ('İtalyan Mətbəxi', 'fas fa-pizza-slice', 'food', False),
            ('Yapon Mətbəxi', 'fas fa-fish', 'food', False),
            ('Çin Mətbəxi', 'fas fa-dragon', 'food', False),
            ('Meksika Mətbəxi', 'fas fa-pepper-hot', 'food', False),
            ('Türk Mətbəxi', 'fas fa-utensils', 'food', False),
            ('Veqan Mətbəx', 'fas fa-leaf', 'food', False),
            ('Vegetarian', 'fas fa-carrot', 'food', False),
            ('Şirniyyat', 'fas fa-cookie', 'food', False),
            ('Tort Bişirmək', 'fas fa-birthday-cake', 'food', False),
            ('Qəhvə', 'fas fa-coffee', 'food', False),
            ('Çay', 'fas fa-mug-hot', 'food', False),
            ('Kokteyillər', 'fas fa-cocktail', 'food', False),
            ('Şərab', 'fas fa-wine-glass', 'food', False),
            ('BBQ', 'fas fa-drumstick-bite', 'food', False),
            ('Manqal', 'fas fa-fire', 'food', False),
            ('Dəniz Məhsulları', 'fas fa-shrimp', 'food', False),
            ('Ət Yeməkləri', 'fas fa-steak', 'food', False),
            ('Fast Food', 'fas fa-hamburger', 'food', False),
            ('Sağlam Qidalanma', 'fas fa-apple-alt', 'food', False),
            
            # Travel & Adventure
            ('Dünya Gəzişi', 'fas fa-globe-americas', 'travel', False),
            ('Kəmpinq', 'fas fa-campground', 'travel', False),
            ('Piyada Gəzinti', 'fas fa-hiking', 'travel', False),
            ('Dağ Gəzintisi', 'fas fa-mountain', 'travel', False),
            ('Sörf', 'fas fa-water', 'travel', False),
            ('Dalğıclıq', 'fas fa-swimmer', 'travel', False),
            ('Paraşütçülük', 'fas fa-parachute-box', 'travel', False),
            ('Qayıq', 'fas fa-ship', 'travel', False),
            ('Kruiz', 'fas fa-anchor', 'travel', False),
            ('Backpacking', 'fas fa-backpack', 'travel', False),
            ('Lüks Səyahət', 'fas fa-hotel', 'travel', False),
            ('Eko Turizm', 'fas fa-tree', 'travel', False),
            ('Safari', 'fas fa-paw', 'travel', False),
            ('Çimərlik', 'fas fa-umbrella-beach', 'travel', False),
            ('Xizək Kurortları', 'fas fa-snowflake', 'travel', False),
            
            # Technology
            ('Proqramlaşdırma', 'fas fa-code', 'tech', False),
            ('Web Development', 'fas fa-laptop-code', 'tech', False),
            ('Mobile Development', 'fas fa-mobile-alt', 'tech', False),
            ('AI və ML', 'fas fa-robot', 'tech', False),
            ('Kriptovalyuta', 'fas fa-bitcoin', 'tech', False),
            ('Blockchain', 'fas fa-link', 'tech', False),
            ('Kibertəhlükəsizlik', 'fas fa-shield-alt', 'tech', False),
            ('Data Science', 'fas fa-database', 'tech', False),
            ('Cloud Computing', 'fas fa-cloud', 'tech', False),
            ('IoT', 'fas fa-microchip', 'tech', False),
            ('Robotika', 'fas fa-cog', 'tech', False),
            ('3D Çap', 'fas fa-print', 'tech', False),
            ('VR/AR', 'fas fa-vr-cardboard', 'tech', False),
            ('Oyun İnkişafı', 'fas fa-dice-d20', 'tech', False),
            ('Hardware', 'fas fa-memory', 'tech', False),
            ('Networking', 'fas fa-network-wired', 'tech', False),
            
            # Music
            ('Pop Musiqi', 'fas fa-music', 'music', True),
            ('Rok Musiqi', 'fas fa-guitar', 'music', True),
            ('Metal Musiqi', 'fas fa-skull', 'music', True),
            ('Jazz', 'fas fa-saxophone', 'music', False),
            ('Klassik Musiqi', 'fas fa-violin', 'music', False),
            ('Elektron Musiqi', 'fas fa-headphones', 'music', True),
            ('Hip-Hop', 'fas fa-microphone', 'music', True),
            ('Rap', 'fas fa-microphone-alt', 'music', False),
            ('R&B', 'fas fa-compact-disc', 'music', False),
            ('Rəqs Musiqisi', 'fas fa-music', 'music', True),
            ('House', 'fas fa-volume-up', 'music', False),
            ('Techno', 'fas fa-music', 'music', False),
            ('Trance', 'fas fa-broadcast-tower', 'music', False),
            ('Heavy Metal', 'fas fa-skull-crossbones', 'music', False),
            ('Death Metal', 'fas fa-skull', 'music', False),
            ('Black Metal', 'fas fa-fire', 'music', False),
            ('Hard Rock', 'fas fa-guitar', 'music', False),
            ('Alternative Rock', 'fas fa-guitar', 'music', False),
            ('Indie Rock', 'fas fa-compact-disc', 'music', False),
            ('Punk Rock', 'fas fa-fist-raised', 'music', False),
            ('Blues', 'fas fa-guitar', 'music', False),
            ('Country', 'fas fa-hat-cowboy-side', 'music', False),
            ('Reggae', 'fas fa-drum', 'music', False),
            ('Muğam', 'fas fa-music', 'music', False),
            ('Aşıq Musiqisi', 'fas fa-guitar', 'music', False),
            ('Xalq Musiqisi', 'fas fa-drum', 'music', False),
            ('Fortepiano', 'fas fa-piano', 'music', False),
            ('Gitara', 'fas fa-guitar', 'music', False),
            ('Nağara', 'fas fa-drum', 'music', False),
            ('Vokal', 'fas fa-microphone', 'music', False),
            ('DJ', 'fas fa-record-vinyl', 'music', False),
            ('Musiqal İstehsal', 'fas fa-sliders-h', 'music', False),
            ('Dubstep', 'fas fa-volume-up', 'music', False),
            ('Drum & Bass', 'fas fa-drum', 'music', False),
            ('Disco', 'fas fa-compact-disc', 'music', False),
            ('Funk', 'fas fa-music', 'music', False),
            ('Soul', 'fas fa-heart', 'music', False),
            
            # Nature & Outdoors
            ('Quş Müşahidəsi', 'fas fa-dove', 'nature', False),
            ('Botanika', 'fas fa-spa', 'nature', False),
            ('Heyvanat Sevgisi', 'fas fa-dog', 'nature', False),
            ('Pişik Sevgisi', 'fas fa-cat', 'nature', False),
            ('Akvaristika', 'fas fa-fish', 'nature', False),
            ('Tərəriçilik', 'fas fa-bee', 'nature', False),
            ('Ətraf Mühit', 'fas fa-globe', 'nature', False),
            ('Ekoloji Təmizlik', 'fas fa-recycle', 'nature', False),
            ('Meşə Gəzintisi', 'fas fa-tree', 'nature', False),
            ('Piknik', 'fas fa-apple-alt', 'nature', False),
            ('Astronomiya', 'fas fa-star', 'nature', False),
            ('Ulduz Müşahidəsi', 'fas fa-moon', 'nature', False),
            ('Meteorologiya', 'fas fa-cloud-sun', 'nature', False),
            ('Geoloji Kəşf', 'fas fa-gem', 'nature', False),
            
            # Education & Learning
            ('Dil Öyrənmə', 'fas fa-language', 'education', False),
            ('Riyaziyyat', 'fas fa-calculator', 'education', False),
            ('Fizika', 'fas fa-atom', 'education', False),
            ('Kimya', 'fas fa-flask', 'education', False),
            ('Biologiya', 'fas fa-dna', 'education', False),
            ('Fəlsəfə', 'fas fa-brain', 'education', False),
            ('Psixologiya', 'fas fa-user-md', 'education', False),
            ('Sosiologiya', 'fas fa-users', 'education', False),
            ('İqtisadiyyat', 'fas fa-chart-line', 'education', False),
            ('Hüquq', 'fas fa-gavel', 'education', False),
            ('Tibb', 'fas fa-stethoscope', 'education', False),
            ('Mühəndislik', 'fas fa-hard-hat', 'education', False),
            ('Memarlıq', 'fas fa-building', 'education', False),
            ('Online Kurslar', 'fas fa-graduation-cap', 'education', False),
            ('Seminarlar', 'fas fa-chalkboard-teacher', 'education', False),
            
            # Health & Wellness
            ('Meditasiya', 'fas fa-om', 'health', False),
            ('Mindfulness', 'fas fa-brain', 'health', False),
            ('Təbii Müalicə', 'fas fa-leaf', 'health', False),
            ('Homeopatiya', 'fas fa-mortar-pestle', 'health', False),
            ('Akupunktur', 'fas fa-syringe', 'health', False),
            ('Masaj', 'fas fa-hand-holding-heart', 'health', False),
            ('Aromterapiya', 'fas fa-wind', 'health', False),
            ('Detoks', 'fas fa-glass-water', 'health', False),
            ('Oruc', 'fas fa-ban', 'health', False),
            ('Vitamin', 'fas fa-pills', 'health', False),
            ('Fitnes Qidalanma', 'fas fa-weight', 'health', False),
            ('Zehni Sağlamlıq', 'fas fa-heart', 'health', False),
            ('Stress İdarəsi', 'fas fa-smile', 'health', False),
            ('Yuxu Higiyenası', 'fas fa-bed', 'health', False),
            
            # Social & Volunteering
            ('Könüllülük', 'fas fa-hands-helping', 'social', False),
            ('Xeyriyyə', 'fas fa-hand-holding-heart', 'social', False),
            ('Sosial Layihələr', 'fas fa-project-diagram', 'social', False),
            ('Ətraf Mühit Təmizliyi', 'fas fa-trash-alt', 'social', False),
            ('Heyvan Qayğısı', 'fas fa-paw', 'social', False),
            ('Uşaq Tərbiyəsi', 'fas fa-child', 'social', False),
            ('Yaşlı Qayğısı', 'fas fa-user-friends', 'social', False),
            ('Sosial Şəbəkələr', 'fas fa-share-alt', 'social', False),
            ('Networking', 'fas fa-handshake', 'social', False),
            ('Public Speaking', 'fas fa-podium', 'social', False),
            ('Liderlik', 'fas fa-crown', 'social', False),
            ('Komanda İşi', 'fas fa-users-cog', 'social', False),
            ('Mentorluq', 'fas fa-user-graduate', 'social', False),
        ]
        
        for name, icon, category, is_general in interests:
            interest, created = Interest.objects.get_or_create(
                name=name,
                defaults={
                    'icon': icon,
                    'category': category,
                    'is_general': is_general
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created interest: {name}'))
            else:
                self.stdout.write(f'Interest already exists: {name}')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Data population completed successfully!'))
        self.stdout.write(f'Total Languages: {Language.objects.count()}')
        self.stdout.write(f'Total Interests: {Interest.objects.count()}')

