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
        ]
        
        for name, code in languages_data:
            language, created = Language.objects.get_or_create(
                code=code,
                defaults={'name': name}
            )
            if created:
                self.stdout.write(f'Created language: {name}')
        
        # Create Interests
        interests_data = [
            ('Dağçılıq', 'fas fa-mountain'),
            ('Fotoqrafiya', 'fas fa-camera'),
            ('Yemək bişirmə', 'fas fa-utensils'),
            ('Səyahət', 'fas fa-plane'),
            ('Musiqi', 'fas fa-music'),
            ('Sənət', 'fas fa-palette'),
            ('İdman', 'fas fa-football-ball'),
            ('Oxumaq', 'fas fa-book'),
            ('Rəqs', 'fas fa-music'),
            ('Yoga', 'fas fa-leaf'),
            ('Velosiped', 'fas fa-bicycle'),
            ('Üzmək', 'fas fa-swimmer'),
            ('Qaçış', 'fas fa-running'),
            ('Oyunlar', 'fas fa-gamepad'),
            ('Kinolar', 'fas fa-film'),
            ('Teatr', 'fas fa-theater-masks'),
            ('Şərab dadmaq', 'fas fa-wine-glass'),
            ('Qəhvə', 'fas fa-coffee'),
            ('Bağçılıq', 'fas fa-seedling'),
            ('Texnologiya', 'fas fa-laptop'),
            ('Dil öyrənmək', 'fas fa-language'),
            ('Könüllülük', 'fas fa-hands-helping'),
            ('Meditasiya', 'fas fa-peace'),
            ('Masa oyunları', 'fas fa-chess'),
            ('Açıq hava macəraları', 'fas fa-tree'),
            ('Çimərlik fəaliyyətləri', 'fas fa-umbrella-beach'),
            ('Qış idmanı', 'fas fa-skiing'),
            ('Balıq tutmaq', 'fas fa-fish'),
            ('Dırmaşma', 'fas fa-mountain'),
            ('Sörf', 'fas fa-water'),
            ('Düşərgə', 'fas fa-campground'),
            ('Yemək və restoran', 'fas fa-hamburger'),
            ('Gecə həyatı', 'fas fa-cocktail'),
            ('Muzeylər', 'fas fa-university'),
            ('Tarix', 'fas fa-landmark'),
            ('Elm', 'fas fa-flask'),
            ('Təbiət', 'fas fa-leaf'),
            ('Heyvanlar', 'fas fa-paw'),
            ('Moda', 'fas fa-tshirt'),
            ('Biznes', 'fas fa-briefcase'),
        ]
        
        for name, icon in interests_data:
            interest, created = Interest.objects.get_or_create(
                name=name,
                defaults={'icon': icon}
            )
            if created:
                self.stdout.write(f'Created interest: {name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up initial data!')
        )
