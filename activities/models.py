from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from PIL import Image

User = get_user_model()


class ActivityCategory(models.Model):
    """Model for activity categories like Sports, Culture, Nature, Art, Food, etc."""
    CATEGORY_CHOICES = [
        ('sports', 'İdman'),
        ('culture', 'Mədəniyyət'),
        ('nature', 'Təbiət'),
        ('art', 'Sənət'),
        ('food', 'Yemək'),
        ('education', 'Təhsil'),
        ('social', 'Sosial'),
        ('entertainment', 'Əyləncə'),
        ('technology', 'Texnologiya'),
        ('music', 'Musiqi'),
        ('photography', 'Fotoqrafiya'),
        ('travel', 'Səyahət'),
        ('business', 'Biznes'),
        ('health', 'Sağlamlıq'),
        ('other', 'Digər'),
    ]
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    icon = models.CharField(max_length=50, default='fas fa-calendar-alt')  # FontAwesome icon class for web
    icon_image = models.ImageField(upload_to='category_icons/', null=True, blank=True)  # Icon image for mobile
    color = models.CharField(max_length=7, default='#5DD3BE')  # Hex color for category badge
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Activity Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Activity(models.Model):
    """Model for activities that users can create and join"""
    
    STATUS_CHOICES = [
        ('draft', 'Qaralama'),
        ('published', 'Yayımlanmış'),
        ('cancelled', 'Ləğv edilmiş'),
        ('completed', 'Tamamlanmış'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Başlanğıc'),
        ('intermediate', 'Orta'),
        ('advanced', 'İrəliləmiş'),
        ('expert', 'Ekspert'),
    ]
    
    DISTRICT_CHOICES = [
        ('nizami', 'Nizami'),
        ('sabail', 'Sabail'),
        ('yasamal', 'Yasamal'),
        ('binagadi', 'Binagadi'),
        ('khazar', 'Xəzər'),
        ('sabunchu', 'Sabunçu'),
        ('surakhani', 'Suraxanı'),
        ('khatai', 'Xətai'),
        ('narimanov', 'Nərimanov'),
        ('nasimi', 'Nəsimi'),
        ('pirallahi', 'Pirallahı'),
        ('other', 'Digər'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    category = models.ForeignKey(ActivityCategory, on_delete=models.CASCADE, related_name='activities')
    description = models.TextField()
    short_description = models.CharField(max_length=300, help_text="Brief description for cards")
    
    # Organizer
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_activities')
    
    # Date and Time
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    duration_hours = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in hours (auto-calculated)")
    
    # Location Information
    location_name = models.CharField(max_length=200, help_text="Name of the venue/location")
    address = models.CharField(max_length=300)
    district = models.CharField(max_length=20, choices=DISTRICT_CHOICES, default='other')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Capacity and Pricing
    max_participants = models.PositiveIntegerField()
    min_participants = models.PositiveIntegerField(default=1)
    is_unlimited_participants = models.BooleanField(default=False, help_text="No limit on participants")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="Price in AZN")
    is_free = models.BooleanField(default=True)
    
    # Activity Details
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    requirements = models.TextField(blank=True, help_text="What participants need to bring or know")
    what_included = models.TextField(blank=True, help_text="What's included in the activity")
    
    # Participant Requirements
    required_languages = models.ManyToManyField('accounts.Language', blank=True, help_text="Languages participants must know")
    allowed_genders = models.JSONField(default=list, blank=True, help_text="Allowed genders for participants")
    min_age = models.PositiveIntegerField(null=True, blank=True, help_text="Minimum age requirement")
    max_age = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum age requirement")
    dress_code = models.CharField(max_length=200, blank=True, help_text="Dress code for the activity")
    gender_balance_required = models.BooleanField(default=False, help_text="Require balanced gender participation")
    
    # Media
    main_image = models.ImageField(upload_to='activities/images/', blank=True, null=True)
    image_alt = models.CharField(max_length=200, blank=True, help_text="Alt text for main image")
    
    # Status and Metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False, help_text="Show in featured activities")
    
    # Contact Information
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', 'start_date']
        indexes = [
            models.Index(fields=['category', 'district']),
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%d/%m/%Y')}"
    
    def get_absolute_url(self):
        return reverse('activities:activity_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        # Auto-calculate duration_hours if not set
        if self.start_date and self.end_date and not self.duration_hours:
            duration = self.end_date - self.start_date
            self.duration_hours = max(1, int(duration.total_seconds() / 3600))
        super().save(*args, **kwargs)
    
    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()
    
    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    @property
    def is_past(self):
        return self.end_date < timezone.now()
    
    def can_user_join(self, user):
        """Check if user meets all requirements to join this activity"""
        if not user.is_authenticated:
            return False, "İlk öncə daxil olmalısınız."
        
        # Check if user is organizer
        if user == self.organizer:
            return False, "Öz aktivitənizə qoşula bilməzsiniz."
        
        # Check if activity is full
        if self.participants.filter(status='approved').count() >= self.max_participants:
            return False, "Aktivitə doludur."
        
        # Check if user already joined or has pending request
        existing_participation = self.participants.filter(user=user).first()
        if existing_participation:
            if existing_participation.status == 'approved':
                return False, "Artıq bu aktivitəyə qoşulmusunuz."
            elif existing_participation.status == 'pending':
                return False, "Sorğunuz gözləyir."
            elif existing_participation.status == 'rejected':
                return False, "Sorğunuz rədd edilib."
        
        # Check age requirements
        if user.age is not None:
            if self.min_age and user.age < self.min_age:
                return False, f"Bu aktivitə üçün minimum yaş {self.min_age}-dir."
            if self.max_age and user.age > self.max_age:
                return False, f"Bu aktivitə üçün maksimum yaş {self.max_age}-dir."
        elif self.min_age or self.max_age:
            return False, "Bu aktivitə üçün yaş məhdudiyyəti var. Profildə doğum tarixinizi göstərin."
        
        # Check gender requirements
        if self.allowed_genders and user.gender:
            if user.gender not in self.allowed_genders:
                gender_names = {'male': 'Kişi', 'female': 'Qadın', 'other': 'Digər', 'prefer_not_to_say': 'Deməyi üstün tutmuram'}
                allowed_names = [gender_names.get(g, g) for g in self.allowed_genders]
                return False, f"Bu aktivitə yalnız {', '.join(allowed_names)} üçündür."
        elif self.allowed_genders and not user.gender:
            return False, "Bu aktivitə üçün cinsiyyət məhdudiyyəti var. Profildə cinsiyyətinizi göstərin."
        
        # Check language requirements
        if self.required_languages.exists():
            user_languages = set(user.languages.all())
            required_languages = set(self.required_languages.all())
            if not required_languages.issubset(user_languages):
                missing_languages = required_languages - user_languages
                missing_names = [lang.name for lang in missing_languages]
                return False, f"Bu aktivitə üçün {', '.join(missing_names)} dil(lər)ini bilməlisiniz."
        
        # Check if activity is in the past
        if self.is_past:
            return False, "Bu aktivitə artıq keçib."
        
        return True, "Qoşula bilərsiniz!"
    
    @property
    def is_full(self):
        return self.participants.filter(status='approved').count() >= self.max_participants
    
    @property
    def available_spots(self):
        approved_count = self.participants.filter(status='approved').count()
        return max(0, self.max_participants - approved_count)
    
    @property
    def participants_count(self):
        return self.participants.filter(status='approved').count()
    
    @property
    def pending_requests_count(self):
        return self.participants.filter(status='pending').count()
    
    def get_status_badge_class(self):
        """Return Bootstrap badge class for status"""
        status_classes = {
            'draft': 'bg-secondary',
            'published': 'bg-success',
            'cancelled': 'bg-danger',
            'completed': 'bg-info'
        }
        return status_classes.get(self.status, 'bg-secondary')
    
    def get_difficulty_badge_class(self):
        """Return Bootstrap badge class for difficulty level"""
        difficulty_classes = {
            'beginner': 'bg-success',
            'intermediate': 'bg-info',
            'advanced': 'bg-warning',
            'expert': 'bg-danger'
        }
        return difficulty_classes.get(self.difficulty_level, 'bg-secondary')
    
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize image if it exists
        if self.main_image:
            img = Image.open(self.main_image.path)
            if img.height > 600 or img.width > 800:
                img.thumbnail((800, 600))
                img.save(self.main_image.path)


class ActivityParticipant(models.Model):
    """Model for tracking activity participants and join requests"""
    
    STATUS_CHOICES = [
        ('pending', 'Gözləmədə'),
        ('approved', 'Təsdiqlənmiş'),
        ('rejected', 'Rədd edilmiş'),
        ('cancelled', 'Ləğv edilmiş'),
    ]
    
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_participations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Join request details
    message = models.TextField(blank=True, help_text="Message from participant to organizer")
    join_requested_at = models.DateTimeField(auto_now_add=True)
    status_updated_at = models.DateTimeField(auto_now=True)
    
    # Organizer response
    organizer_response = models.TextField(blank=True, help_text="Response from organizer")
    
    class Meta:
        unique_together = ['activity', 'user']
        ordering = ['-join_requested_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.activity.title} ({self.status})"
    
    def get_status_badge_class(self):
        status_classes = {
            'pending': 'bg-warning',
            'approved': 'bg-success',
            'rejected': 'bg-danger',
            'cancelled': 'bg-secondary'
        }
        return status_classes.get(self.status, 'bg-secondary')


class ActivityImage(models.Model):
    """Additional images for activities"""
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='activities/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"{self.activity.title} - Image {self.id}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize image
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 600 or img.width > 800:
                img.thumbnail((800, 600))
                img.save(self.image.path)


class ActivityReview(models.Model):
    """Reviews for completed activities"""
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    
    # Only participants who attended can review
    participant = models.OneToOneField(ActivityParticipant, on_delete=models.CASCADE, related_name='review')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['activity', 'reviewer']
    
    def __str__(self):
        return f"{self.activity.title} - {self.rating} stars by {self.reviewer.get_full_name()}"
    
    def get_rating_stars(self):
        """Return filled and empty stars for rating display"""
        full_stars = self.rating
        empty_stars = 5 - full_stars
        return {
            'full': range(full_stars),
            'empty': range(empty_stars)
        }


class ActivityComment(models.Model):
    """Comments and discussions for activities"""
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_comments')
    comment = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.activity.title}"
    
    @property
    def is_reply(self):
        return self.parent is not None


class ActivityMessage(models.Model):
    """Chat messages for activities - only for joined participants"""
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_messages')
    message = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['activity', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} in {self.activity.title}: {self.message[:50]}..."
    
    def can_edit(self, user):
        """Check if user can edit this message"""
        return self.user == user
    
    def can_delete(self, user):
        """Check if user can delete this message"""
        return self.user == user or user == self.activity.organizer