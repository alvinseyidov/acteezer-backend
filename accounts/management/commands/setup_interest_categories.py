from django.core.management.base import BaseCommand
from accounts.models import InterestCategory, Interest


class Command(BaseCommand):
    help = 'Create default interest categories and interests in Azerbaijani'

    def handle(self, *args, **options):
        self.stdout.write('Creating interest categories and interests...')
        
        # Category definitions with Azerbaijani names
        categories_data = [
            {
                'code': 'sports',
                'name': 'İdman & Fitnes',
                'icon': 'fas fa-running',
                'order': 1,
                'interests': [
                    'Futbol', 'Basketbol', 'Voleybol', 'Tennis', 'Üzgüçülük',
                    'Fitness', 'Yoga', 'Pilates', 'Boks', 'MMA',
                    'Velosiped sürmə', 'Qaçış', 'Alpinizm', 'Şahmat',
                    'Badminton', 'Stolüstü tennis', 'Güləş', 'Karate',
                    'Gimnastika', 'Atletika', 'Xizək', 'Skeyt'
                ]
            },
            {
                'code': 'music',
                'name': 'Musiqi',
                'icon': 'fas fa-music',
                'order': 2,
                'interests': [
                    'Gitara', 'Piano', 'Violin', 'Nağara', 'Tar',
                    'Kamança', 'Saz', 'Pop musiqi', 'Rok musiqi', 'Caz',
                    'Klassik musiqi', 'Xalq musiqisi', 'Muğam', 'DJ',
                    'Mahnı oxumaq', 'Xor', 'Musiqi prodüserliyi'
                ]
            },
            {
                'code': 'arts',
                'name': 'Sənət & Mədəniyyət',
                'icon': 'fas fa-palette',
                'order': 3,
                'interests': [
                    'Rəssamlıq', 'Heykəltəraşlıq', 'Fotoqrafiya', 'Kino',
                    'Teatr', 'Rəqs', 'Balet', 'Opera', 'Xalq rəqsləri',
                    'Yazıçılıq', 'Şeir', 'Dizayn', 'Qrafik dizayn',
                    'İnteryer dizayn', 'Moda dizayn', 'Keramika', 'Toxuculuq',
                    'Xəttatlıq', 'Kinematoqrafiya', 'Animasiya'
                ]
            },
            {
                'code': 'food',
                'name': 'Yemək & Qəlyanaltı',
                'icon': 'fas fa-utensils',
                'order': 4,
                'interests': [
                    'Aşbazlıq', 'Şirniyyat hazırlamaq', 'Milli mətbəx',
                    'İtalyan mətbəxi', 'Asiya mətbəxi', 'Şərq mətbəxi',
                    'Sağlam qidalanma', 'Vegetarian', 'Vegan',
                    'Barista', 'Şərabçılıq', 'Restoran kəşfi',
                    'Street food', 'Barbekü', 'Desertlər'
                ]
            },
            {
                'code': 'travel',
                'name': 'Səyahət & Macəra',
                'icon': 'fas fa-plane',
                'order': 5,
                'interests': [
                    'Xarici ölkələrə səyahət', 'Yerli turizm', 'Dağ turizmi',
                    'Çimərlik istirahəti', 'Kempinq', 'Avtostop',
                    'Mədəni turizm', 'Tarixi yerlər', 'Fotosəyahət',
                    'Solo səyahət', 'Qrup turları', 'Ekoturizm',
                    'Motosiklet səyahəti', 'Kruiz', 'Backpacking'
                ]
            },
            {
                'code': 'nature',
                'name': 'Təbiət & Açıq Hava',
                'icon': 'fas fa-leaf',
                'order': 6,
                'interests': [
                    'Hiking', 'Piknik', 'Bağçılıq', 'Balıq tutma',
                    'Ov', 'Quşlara baxış', 'Təbiət fotoqrafiyası',
                    'Kempinq', 'Dağa dırmanma', 'Mağara kəşfi',
                    'Çay enişi', 'At minmə', 'Ekologiya',
                    'Heyvanlar', 'Bitkilər', 'Meşə gəzintisi'
                ]
            },
            {
                'code': 'tech',
                'name': 'Texnologiya',
                'icon': 'fas fa-laptop-code',
                'order': 7,
                'interests': [
                    'Proqramlaşdırma', 'Veb dizayn', 'Mobil proqramlar',
                    'Süni intellekt', 'Data Science', 'Kibertəhlükəsizlik',
                    'Video oyunları', 'E-idman', 'Robototexnika',
                    'Dronlar', '3D çap', 'VR/AR', 'Blockchain',
                    'Startaplar', 'Texnoloji yeniliklər', 'Gadget-lər'
                ]
            },
            {
                'code': 'beauty',
                'name': 'Gözəllik & Moda',
                'icon': 'fas fa-gem',
                'order': 8,
                'interests': [
                    'Makiyaj', 'Saç baxımı', 'Dəri baxımı', 'Moda',
                    'Geyim stili', 'Aksessuarlar', 'Dırnaq dizaynı',
                    'Parfümeriya', 'Modellik', 'Moda fotoqrafiyası',
                    'Stil məsləhətçiliyi', 'Gözəllik bloqqerliyi',
                    'Saç düzümü', 'Spa prosedurları'
                ]
            },
            {
                'code': 'lifestyle',
                'name': 'Həyat Tərzi',
                'icon': 'fas fa-home',
                'order': 9,
                'interests': [
                    'Ev dekoru', 'DIY layihələri', 'Minimalizm',
                    'Şəxsi inkişaf', 'Meditasiya', 'Mindfulness',
                    'Kitab oxumaq', 'Podkastlar', 'Jurnal yazma',
                    'Əl işləri', 'Antik əşyalar', 'Kolleksiyaçılıq',
                    'Ev heyvanları', 'Vaxt idarəetməsi', 'Həyat bacarıqları'
                ]
            },
            {
                'code': 'education',
                'name': 'Təhsil & Öyrənmə',
                'icon': 'fas fa-graduation-cap',
                'order': 10,
                'interests': [
                    'Dil öyrənmə', 'İngilis dili', 'Rus dili', 'Türk dili',
                    'Tarix', 'Fəlsəfə', 'Psixologiya', 'İqtisadiyyat',
                    'Biznes', 'Marketinq', 'Liderlik', 'Natiqlik',
                    'Onlayn kurslar', 'Kitab klubları', 'Seminarlar',
                    'Mentorluq', 'Karyera inkişafı'
                ]
            },
            {
                'code': 'health',
                'name': 'Sağlamlıq',
                'icon': 'fas fa-heartbeat',
                'order': 11,
                'interests': [
                    'Sağlam həyat tərzi', 'Pəhriz', 'Detoks',
                    'Meditasiya', 'Stress idarəetməsi', 'Yuxu sağlamlığı',
                    'Mental sağlamlıq', 'Alternativ təbabət',
                    'Masaj', 'Akupunktur', 'Homeopatiya',
                    'Fitoterapiya', 'Sağlamlıq bloqqerliyi'
                ]
            },
            {
                'code': 'social',
                'name': 'Sosial & Könüllülük',
                'icon': 'fas fa-hands-helping',
                'order': 12,
                'interests': [
                    'Könüllülük', 'Xeyriyyəçilik', 'İcma xidməti',
                    'Ekoloji fəaliyyət', 'Heyvan himayəsi',
                    'Uşaq tərbiyəsi', 'Yaşlılara yardım', 'Networking',
                    'Sosial tədbirlər', 'Qrup fəaliyyətləri',
                    'Mədəni mübadilə', 'Beynəlxalq dostluq'
                ]
            },
        ]
        
        created_categories = 0
        created_interests = 0
        
        for cat_data in categories_data:
            # Create or update category
            category, created = InterestCategory.objects.update_or_create(
                code=cat_data['code'],
                defaults={
                    'name': cat_data['name'],
                    'icon': cat_data['icon'],
                    'order': cat_data['order'],
                    'is_active': True
                }
            )
            
            if created:
                created_categories += 1
                self.stdout.write(f'  ✓ Created category: {category.name}')
            else:
                self.stdout.write(f'  ↻ Updated category: {category.name}')
            
            # Create interests for this category
            for interest_name in cat_data['interests']:
                interest, int_created = Interest.objects.get_or_create(
                    name=interest_name,
                    defaults={
                        'category': category,
                        'is_general': False
                    }
                )
                
                if int_created:
                    created_interests += 1
                else:
                    # Update existing interest's category if it was None
                    if interest.category is None:
                        interest.category = category
                        interest.save()
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Done! Created {created_categories} categories and {created_interests} interests.'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Total categories: {InterestCategory.objects.count()}'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Total interests: {Interest.objects.count()}'
        ))

