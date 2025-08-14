from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from accounts.models import User, BlogCategory, BlogPost, BlogTag, BlogPostTag
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample blog posts related to activity topics in Baku'

    def handle(self, *args, **options):
        # Create categories
        categories_data = [
            {'name': 'İdman və Aktivitə', 'slug': 'idman-aktivite', 'description': 'İdman və fiziki aktivitələr haqqında'},
            {'name': 'Mədəniyyət və Sənət', 'slug': 'medeniyyet-senet', 'description': 'Mədəni tədbirlər və sənət fəaliyyətləri'},
            {'name': 'Təbiət və Səyahət', 'slug': 'tebiet-seyahet', 'description': 'Təbiət gəzintiləri və səyahət təcrübələri'},
            {'name': 'Yemək və Kulinariya', 'slug': 'yemek-kulinariya', 'description': 'Yemək festivalları və kulinariya təcrübələri'},
            {'name': 'Şəhər Həyatı', 'slug': 'sheher-heyati', 'description': 'Bakı şəhər həyatı və icma fəaliyyətləri'},
        ]

        categories = {}
        for cat_data in categories_data:
            category, created = BlogCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name'], 'description': cat_data['description']}
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(f"Created category: {category.name}")

        # Create tags
        tags_data = [
            'bakı', 'aktivitə', 'idman', 'təbiət', 'mədəniyyət', 'yemək', 
            'səyahət', 'dostluq', 'icma', 'təcrübə', 'macəra', 'sənət',
            'həftəsonu', 'planlaşdırma', 'əyləncə', 'kulinariya', 'restoran', 'gecə'
        ]

        tags = {}
        for tag_name in tags_data:
            tag, created = BlogTag.objects.get_or_create(
                slug=slugify(tag_name),
                defaults={'name': tag_name}
            )
            tags[tag_name] = tag
            if created:
                self.stdout.write(f"Created tag: {tag.name}")

        # Get or create a default author (admin user)
        try:
            author = User.objects.filter(is_superuser=True).first()
            if not author:
                author = User.objects.create_user(
                    phone='+994501234567',
                    first_name='Admin',
                    last_name='User',
                    is_staff=True,
                    is_superuser=True,
                    is_phone_verified=True,
                    is_registration_complete=True,
                    registration_step=8
                )
                self.stdout.write("Created admin user for blog posts")
        except Exception as e:
            self.stdout.write(f"Error creating author: {e}")
            return

        # Blog posts data
        blog_posts_data = [
            {
                'title': 'Bakıda Ən Yaxşı İdman Aktivitələri',
                'category': 'idman-aktivite',
                'excerpt': 'Şəhərimizdə həftə sonları keçirilən idman fəaliyyətləri və qruplarına qoşulma yolları haqqında ətraflı məlumat.',
                'content': '''
Bakı şəhərində idman aktivitələri getdikcə populyarlaşır. Xüsusilə iqlimin yaxşı olduğu aylar ərzində çoxlu sayda idman həvəskarları müxtəlif fəaliyyətlərə qatılır.

## Ən Populyar İdman Aktivitələri

### 1. Səhər Qaçışları
Hər həftə Bulvar boyunca təşkil edilən səhər qaçışları şəhərin ən populyar aktivitələrindən biridir. Qrup halında qaçış təkcə fiziki sağlamlığa deyil, həm də sosial əlaqələrin qurulmasına kömək edir.

### 2. Yoga Seansları
Dənizkənarı parkda keçirilən yoga seansları artan maraqla qarşılanır. Təcrübəli təlimatçıların rəhbərliyi altında həm başlayanlar, həm də inkişaf etmiş iştirakçılar üçün uyğun proqramlar təklif edilir.

### 3. Futbol Turnirləri
Məhəllə komandaları arasında keçirilən mini futbol turnirləri gənclər arasında böyük populyarlıq qazanıb. Bu turnirlərdə yeni dostluqlar qurulur və komanda ruhu inkişaf edir.

## Qoşulma Yolları

Bu aktivitələrə qoşulmaq üçün:
- Acteezer platformasından qeydiyyat keçirin
- Maraq dairənizi seçin
- Həftəlik proqrama baxın və uyğun vaxtı seçin

İdman etmək həm sağlamlıq, həm də sosial əlaqələr üçün vacibdir. Bizə qoşulun və aktiv həyat yaşayın!
                ''',
                'tags': ['bakı', 'idman', 'aktivitə', 'dostluq'],
                'is_featured': True,
            },
            {
                'title': 'Bakı Mədəniyyət Həyatında Yeni Trendlər',
                'category': 'medeniyyet-senet',
                'excerpt': 'Şəhərin mədəni həyatında baş verən dəyişikliklər və gənclərin mədəniyyətə olan marağının artması.',
                'content': '''
Son illər Bakının mədəni həyatında əhəmiyyətli dəyişikliklər baş verir. Gənclər arasında ənənəvi və müasir sənət növlərinə maraq artır.

## Ən Aktiv Sahələr

### Musiqi və Konsertlər
Canlı musiqi gecələri və akustik performanslar gənclərin ən çox sevdiyi tədbirlər arasındadır. 

### Sənət Emalatxanaları
Emalatxana formatında keçirilən yaradıcılıq dərnələri iştirakçıların yeni bacarıqlar öyrənməsinə imkan yaradır.

### Mədəni Gəzintilər
İçəri Şəhər və digər tarixi məkanların kəşfi formatında təşkil edilən gəzintilər böyük maraqla qarşılanır.

Bu fəaliyyətlər vasitəsilə insanlar həm öz yaradıcı potensiallarını açır, həm də həmfikir dostlar tapır.
                ''',
                'tags': ['mədəniyyət', 'sənət', 'bakı', 'təcrübə'],
                'is_featured': False,
            },
            {
                'title': 'Abşeron Yarımadasında Təbiət Gəzintiləri',
                'category': 'tebiet-seyahet',
                'excerpt': 'Bakı ətrafındaki təbii gözəlliklərin kəşfi və qrup gəzintilərinin təşkili haqqında tövsiyələr.',
                'content': '''
Abşeron yarımadası təbii gözəllikləri ilə zəngindir. Şəhərlik həyatından yorulan insanlar üçün təbiətə səyahət əla həll yoludur.

## Tövsiyə Edilən Yerlər

### Qobustan Milli Parkı
Qədim qaya rəsmləri və palçıq vulkanları ilə məşhur olan bu yer əsl təbiət həvəskarları üçün ideal məkandır.

### Yanar Dağ
Gecə vaxtı ziyarət üçün ən yaxşı yerlərdən biri olan Yanar Dağ romantik və mistik atmosfer yaradır.

### Şıxov çimərliyi
Yay aylarında istirahət və su idmanları üçün populyar məkandır.

### Gəzinti Təhlükəsizliyi
Qrup halında gəzinti həm təhlükəsizlik, həm də əyləncəli vaxt keçirmək baxımından daha yaxşıdır.

Təbiətin qoynunda keçirilən vaxt həm fiziki, həm də mənəvi sağlamlıq üçün çox faydalıdır.
                ''',
                'tags': ['təbiət', 'səyahət', 'abşeron', 'macəra'],
                'is_featured': False,
            },
            {
                'title': 'Bakı Kulinariya Festivalarına Bələdçi',
                'category': 'yemek-kulinariya',
                'excerpt': 'Şəhərdə keçirilən kulinariya tədbirləri və milli mətbəx festivallarında iştirak etmək üçün məsləhətlər.',
                'content': '''
Bakının kulinariya səhnəsi getdikcə rəngarəngləşir. Milli mətbəximizin tanıdılması və populyarlaşdırılması istiqamətində aparılan işlər sevindiricidir.

## Festival Növləri

### Milli Mətbəx Festivalları
Azərbaycan mətbəxinin ən dadlı yeməklərinin nümayiş etdirildiyi bu tədbirlər həm yerli, həm də xarici qonaqların marağını çəkir.

### Beynəlxalq Kulinariya Gecələri
Müxtəlif ölkələrin mətbəxlərini tanımaq üçün keçirilən bu tədbirdə iştirakçılar yeni dadlar kəşf edir.

### Aşpazlıq Masterklassları
Təcrübəli aşpazların rəhbərliyi altında keçirilən dərslər kulinariya bacarıqlarınızı inkişaf etdirmək üçün əla fürsətdir.

## İştirak Üçün Məsləhətlər
- Vaxtında qeydiyyat edin
- Açıq ürəklə yeni dadları sınayın  
- Aşpazlarla söhbət edin və reseptlər öyrənin
- Təəssüratlarınızı digərləri ilə bölüşün

Kulinariya həm ləzzət, həm də mədəni mübadilədir.
                ''',
                'tags': ['yemək', 'kulinariya', 'festival', 'mədəniyyət'],
                'is_featured': False,
            },
            {
                'title': 'Bakı Gənclərinin Icma Fəaliyyətləri',
                'category': 'sheher-heyati',
                'excerpt': 'Şəhər gənclərinin könüllü fəaliyyətləri və icma layihələrində iştirakın faydaları.',
                'content': '''
Bakı gəncləri arasında icma fəaliyyətlərinə maraq artır. Bu, həm şəxsi inkişaf, həm də sosial məsuliyyət hissi baxımından olduqca əhəmiyyətlidir.

## Əsas İstiqamətlər

### Ekoloji Aksiyalar
Ətraf mühitin qorunması üçün keçirilən təmizlik aksiyaları və ağacəkmə kampaniyaları gənclərin ən aktiv iştirak etdiyi tədbirlərdir.

### Yaşlılara Yardım
Yaşlı insanlara köməklik göstərmək istiqamətində aparılan fəaliyyətlər sosial həmrəyliyi möhkəmləndirir.

### Uşaq Layihələri
Uşaq evləri və məktəblərdə keçirilən könüllü fəaliyyətlər gənclərin empatiya qabiliyyətini inkişaf etdirir.

### Mədəni İrs
Tarixi abidələrin və mədəni irsin qorunması istiqamətində aparılan işlər milli şüuru gücləndirir.

## Qoşulmanın Faydaları
- Liderlik bacarıqlarının inkişafı
- Yeni dostluqların qurulması
- Sosial məsuliyyət hissinin güclənməsi
- Şəxsi və peşəkar inkişaf

İcma fəaliyyətləri həm cəmiyyət, həm də şəxs üçün faydalıdır.
                ''',
                'tags': ['icma', 'gənclər', 'könüllülük', 'sosial'],
                'is_featured': False,
            },
            {
                'title': 'Həftə Sonu Aktivitələri: Bakıda Nə Etmək Olar?',
                'category': 'sheher-heyati',
                'excerpt': 'Həftə sonları Bakıda keçirilə biləcək maraqlı aktivitələr və təkliflər siyahısı.',
                'content': '''
Həftə sonu planı düşünürkən çox vaxt çətinlik çəkirik. Bakıda isə hər həftə sonu üçün müxtəlif seçimlər mövcuddur.

## Səhər Aktivitələri

### Erkən Səhər Yoga
Gün başlanğıcını sakit və energili keçirmək üçün səhər yoga seansları ideal seçimdir.

### Dənizkənarı Gəzintisi
Təmiz havanın və dəniz nəsiminin həzz aldığı səhər gəzintiləri ruhu dincləndirir.

## Gündüz Fəaliyyətləri

### Muzey Ziyarətləri
Şəhərin zəngin tarixi və mədəni irsi ilə tanış olmaq üçün muzey ziyarətləri tövsiyə edilir.

### Şəhər Velosiped Turları
Qrup halında şəhəri velosipedlə gəzmək həm idman, həm də kəşfiyyat deməkdir.

## Axşam Əyləncələri

### Akustik Konsertlər
Kiçik məkanlarda keçirilən intimy konsertler musiqi həvəskarları üçün xoş təcrübədir.

### Kinogecələr
Açıq havada və ya kiçik kinozallarda film seyrətmək dostlarla keyfiyyətli vaxt keçirməyin yoludur.

Həftə sonunu planlaşdırarkən öz maraqlarınızı nəzərə alın və yeni təcrübələrə açıq olun.
                ''',
                'tags': ['həftəsonu', 'planlaşdırma', 'əyləncə', 'aktivitə'],
                'is_featured': False,
            },
            {
                'title': 'Bakı Gecələri: Şəhərin Gecə Həyatı və Əyləncələri',
                'category': 'sheher-heyati',
                'excerpt': 'Bakının gecə həyatını kəşf edin - restoranlardan tutmuş gecə klublarına qədər hər şey.',
                'content': '''
Bakı gün batımından sonra tamamilə fərqli bir simaya bürünür. Şəhərin gecə həyatı müxtəlif yaş qrupları və zövqlər üçün zəngin təcrübələr təklif edir.

## Gecə Mənzərəli Restoranlar

Bakının ən gözəl gecə mənzərələrini seyredərək yemək yeyə biləcəyiniz restoranlar şəhərin ən romantik yerləridir. Flame Towers-in işıqları altında, Xəzər dənizinin sahilində yerləşən restoranlarda yerli və beynəlxalq mətbəx nümunələrini dada bilərsiniz.

### Tövsiyə Edilən Məkanlar
- Rooftop restoranları - Şəhər panoraması
- Dənizkənarı restoranlar - Dəniz mənzərəsi  
- Tarixi mərkəz kafeləri - Nostaljik atmosfer
- Modern bistro və wine barları

## Dənizkənarı Bulvar Gecə Gəzintiləri

Bakı Bulvarı gecələr də həyat dolu olur. İşıqlandırılmış yollar, fıskiyələr və dəniz mənzərəsi ilə gecə gəzintisi etmək şəhərin ən sevimli aktivitələrindən biridir.

### Bulvarda Gecə Fəaliyyətləri
- Romantik gəzinti yolları
- Açıq havada çay evləri
- Gece konsertləri və performanslar  
- Fıskiyə şoularının seyriyyəti

## Gecə Klubları və Bar Mədəniyyəti

Bakının gecə klubları müxtəlif musiqi janrları və atmosfer təklif edir. Elektronik musiqidən caz klublarına, karaoke barlara qədər hər zövqə uyğun məkanlar var.

### Klub Növləri
- **Elektronik musiqi klubları** - DJ performansları
- **Caz klubları** - Intimy atmosfer
- **Lounge barları** - Rahat söhbət mühiti
- **Karaoke məkanları** - Dostlarla əyləncə

## Mədəni Gecə Tədbirləri

Bakının mədəni gecə həyatı çox zəngindir:
- Opera və balet tamaşaları
- Gecə muzey turları  
- Art qalereyalarda açılışlar
- Ədəbi gecələr və kitab təqdimatları

## Təhlükəsizlik Məsləhətləri

Gecə çıxarkən təhlükəsizlik önəmlidir:
- Yaxşı işıqlandırılmış yerləri seçin
- Dostlarınızla birlikdə gedin
- Təhlükəsiz nəqliyyat planlaşdırın
- Şəxsi əşyalarınıza diqqət edin
- Alkohol istifadəsində ölçülü olun

Bakı gecələri şəhərin əsl ruhunu kəşf etmək üçün ideal vaxtdır. Hər zövqə uyğun təcrübə və unudulmaz anılar bizi gözləyir.
                ''',
                'tags': ['bakı', 'əyləncə', 'gecə', 'restoran', 'mədəniyyət'],
                'is_featured': False,
            },
        ]

        # Create blog posts
        created_posts = []
        for i, post_data in enumerate(blog_posts_data):
            # Create unique slug
            base_slug = slugify(post_data['title'])
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            # Set published date (spread over last 30 days)
            published_date = timezone.now() - timedelta(days=random.randint(1, 30))

            post, created = BlogPost.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': post_data['title'],
                    'author': author,
                    'category': categories[post_data['category']],
                    'excerpt': post_data['excerpt'],
                    'content': post_data['content'],
                    'is_published': True,
                    'is_featured': post_data['is_featured'],
                    'published_at': published_date,
                    'views_count': random.randint(50, 500),
                }
            )

            if created:
                created_posts.append(post)
                self.stdout.write(f"Created blog post: {post.title}")

                # Add tags
                for tag_name in post_data['tags']:
                    if tag_name in tags:
                        BlogPostTag.objects.get_or_create(
                            post=post,
                            tag=tags[tag_name]
                        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(created_posts)} blog posts!')
        )
