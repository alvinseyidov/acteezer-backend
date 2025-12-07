from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
import os


class UserManager(BaseUserManager):
    """Custom user manager for phone-based authentication"""
    
    def create_user(self, phone, first_name='', last_name='', password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        
        user = self.model(
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_phone_verified', True)
        extra_fields.setdefault('is_registration_complete', True)
        extra_fields.setdefault('registration_step', 8)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone, first_name, last_name, password, **extra_fields)


def user_image_path(instance, filename):
    """Generate file path for user image uploads"""
    ext = filename.split('.')[-1]
    filename = f'user_{instance.id}_{filename}'
    return os.path.join('users/images/', filename)


class Language(models.Model):
    """Model for languages that users can know"""
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=5, unique=True)  # e.g., 'en', 'es', 'fr'
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class InterestCategory(models.Model):
    """Model for interest categories - manageable from admin"""
    name = models.CharField(max_length=100, unique=True, help_text="Display name (e.g., 'İdman & Fitnes')")
    code = models.SlugField(max_length=50, unique=True, help_text="Unique code (e.g., 'sports')")
    icon = models.CharField(max_length=100, default='fas fa-star', help_text="Font Awesome icon class (e.g., 'fas fa-running')")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower = first)")
    is_active = models.BooleanField(default=True, help_text="Show this category in registration")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Interest Category"
        verbose_name_plural = "Interest Categories"
        ordering = ['order', 'name']


class Interest(models.Model):
    """Model for user interests"""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, null=True)  # Font awesome icon name or emoji
    icon_image = models.ImageField(upload_to='interest_icons/', null=True, blank=True, help_text="Icon image for interest")
    category = models.ForeignKey(
        InterestCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='interests',
        help_text="Category this interest belongs to"
    )
    is_general = models.BooleanField(default=False, help_text="Show in general/popular section")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class User(AbstractUser):
    """Extended User model for step-by-step registration"""
    
    # Phone validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    # Gender choices
    GENDER_CHOICES = [
        ('male', 'Kişi'),
        ('female', 'Qadın'),
        ('other', 'Digər'),
        ('prefer_not_to_say', 'Deməyi üstün tutmuram'),
    ]
    
    # Registration steps
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True)
    is_phone_verified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    
    # Google OAuth fields
    is_google_signup = models.BooleanField(default=False, help_text="True if user registered via Google OAuth")
    
    # Personal information
    birthday = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    
    # Languages
    languages = models.ManyToManyField(Language, blank=True)
    
    # Location
    city = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Interests
    interests = models.ManyToManyField(Interest, blank=True)
    
    # Registration completion tracking
    registration_step = models.IntegerField(default=0)  # 0: phone, 1: otp, 2: name, 3: languages, 4: birthday, 5: images, 6: bio, 7: interests, 8: location, 9: complete
    is_registration_complete = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Override username requirement
    username = None
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.phone} - {self.get_full_name()}"
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.phone
    
    @property
    def age(self):
        if self.birthday:
            from datetime import date
            today = date.today()
            return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        return None


class UserImage(models.Model):
    """Model for user profile images (minimum 2 required)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=user_image_path)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'uploaded_at']
        unique_together = ['user', 'order']
    
    def __str__(self):
        return f"{self.user.phone} - Image {self.order}"
    
    def save(self, *args, **kwargs):
        # If this is the first image, make it primary
        if not self.user.images.exists():
            self.is_primary = True
            self.order = 1
        elif self.order == 0:
            # Auto-assign order if not set
            last_order = self.user.images.aggregate(models.Max('order'))['order__max'] or 0
            self.order = last_order + 1
        
        super().save(*args, **kwargs)
        
        # Ensure only one primary image
        if self.is_primary:
            UserImage.objects.filter(user=self.user).exclude(id=self.id).update(is_primary=False)


class OTPVerification(models.Model):
    """Model to track OTP verification attempts"""
    PURPOSE_CHOICES = [
        ('registration', 'Registration'),
        ('login', 'Login'),
        ('password_reset', 'Password Reset'),
    ]
    
    phone = models.CharField(max_length=17)
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=15, choices=PURPOSE_CHOICES, default='registration')
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.phone} - {self.otp_code}"


def blog_image_path(instance, filename):
    """Generate file path for blog image uploads"""
    ext = filename.split('.')[-1]
    filename = f'blog_{instance.id}_{filename}'
    return os.path.join('blogs/images/', filename)


class BlogCategory(models.Model):
    """Model for blog categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """Model for blog posts"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name='posts')
    excerpt = models.TextField(max_length=300, help_text="Brief description of the blog post")
    content = models.TextField()
    featured_image = models.ImageField(upload_to=blog_image_path, blank=True, null=True)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"/blog/{self.slug}/"
    
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])


class BlogTag(models.Model):
    """Model for blog tags"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name


class BlogPostTag(models.Model):
    """Many-to-many relationship between blog posts and tags"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='tags')
    tag = models.ForeignKey(BlogTag, on_delete=models.CASCADE, related_name='posts')
    
    class Meta:
        unique_together = ('post', 'tag')


class Friendship(models.Model):
    """Model for friendship relationships between users"""
    FRIENDSHIP_STATUS_CHOICES = [
        ('pending', 'Gözləyir'),
        ('accepted', 'Qəbul edildi'),
        ('rejected', 'Rədd edildi'),
        ('blocked', 'Bloklandı'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=10, choices=FRIENDSHIP_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.get_full_name()} → {self.to_user.get_full_name()} ({self.get_status_display()})"
    
    @classmethod
    def are_friends(cls, user1, user2):
        """Check if two users are friends"""
        return cls.objects.filter(
            models.Q(from_user=user1, to_user=user2, status='accepted') |
            models.Q(from_user=user2, to_user=user1, status='accepted')
        ).exists()
    
    @classmethod
    def get_friendship_status(cls, user1, user2):
        """Get friendship status between two users"""
        friendship = cls.objects.filter(
            models.Q(from_user=user1, to_user=user2) |
            models.Q(from_user=user2, to_user=user1)
        ).first()
        
        if not friendship:
            return None
        
        # Return status and who initiated
        return {
            'status': friendship.status,
            'initiated_by': friendship.from_user,
            'friendship': friendship
        }
    
    @classmethod
    def get_friends(cls, user):
        """Get all friends of a user"""
        friend_ids = cls.objects.filter(
            models.Q(from_user=user, status='accepted') |
            models.Q(to_user=user, status='accepted')
        ).values_list('from_user_id', 'to_user_id')
        
        all_friend_ids = set()
        for from_id, to_id in friend_ids:
            if from_id == user.id:
                all_friend_ids.add(to_id)
            else:
                all_friend_ids.add(from_id)
        
        return User.objects.filter(id__in=all_friend_ids)


class Newsletter(models.Model):
    """Model for newsletter subscriptions"""
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='newsletter_subscriptions')
    
    class Meta:
        ordering = ['-subscribed_at']
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"
    
    def __str__(self):
        return f"{self.email} - {'Active' if self.is_active else 'Inactive'}"


class NotificationSettings(models.Model):
    """Model for user notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Friend-related notifications
    friend_requests = models.BooleanField(default=True, help_text="Yeni dostluq sorğuları")
    friend_request_accepted = models.BooleanField(default=True, help_text="Dostluq sorğusu qəbul edildi")
    friend_new_activity = models.BooleanField(default=True, help_text="Dostlarım yeni aktivitə yaratdı")
    
    # Activity-related notifications (for organizers)
    activity_join_request = models.BooleanField(default=True, help_text="Aktivitə qoşulma sorğusu")
    activity_participant_left = models.BooleanField(default=True, help_text="İştirakçı aktivitəni tərk etdi")
    activity_comment = models.BooleanField(default=True, help_text="Aktivitəyə yeni şərh")
    
    # Activity-related notifications (for participants)
    activity_update = models.BooleanField(default=True, help_text="Qatıldığım aktivitədə dəyişiklik")
    activity_cancelled = models.BooleanField(default=True, help_text="Aktivitə ləğv edildi")
    activity_reminder = models.BooleanField(default=True, help_text="Aktivitə xatırlatması (1 gün əvvəl)")
    
    # Discovery notifications
    new_activities_nearby = models.BooleanField(default=True, help_text="Yaxınlıqda yeni aktivitələr")
    new_activities_interests = models.BooleanField(default=True, help_text="Maraqlarıma uyğun yeni aktivitələr")
    
    # Message notifications
    new_message = models.BooleanField(default=True, help_text="Yeni mesaj bildirişi")
    
    # System notifications
    system_updates = models.BooleanField(default=True, help_text="Sistem yenilikləri")
    promotional = models.BooleanField(default=False, help_text="Reklam və təkliflər")
    
    # Notification delivery preferences
    push_enabled = models.BooleanField(default=True, help_text="Push bildirişlərini aktivləşdir")
    email_enabled = models.BooleanField(default=False, help_text="Email bildirişlərini aktivləşdir")
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False, help_text="Səssiz saatları aktivləşdir")
    quiet_hours_start = models.TimeField(default='22:00', help_text="Səssiz saatların başlanğıcı")
    quiet_hours_end = models.TimeField(default='08:00', help_text="Səssiz saatların sonu")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Notification Settings"
        verbose_name_plural = "Notification Settings"
    
    def __str__(self):
        return f"Notification Settings for {self.user.get_full_name()}"


class PushToken(models.Model):
    """Model to store user push notification tokens"""
    PLATFORM_CHOICES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_tokens')
    token = models.CharField(max_length=255, unique=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    device_name = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Push Token"
        verbose_name_plural = "Push Tokens"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.platform} ({self.token[:20]}...)"


class Notification(models.Model):
    """Model for storing user notifications"""
    NOTIFICATION_TYPES = [
        # Friend notifications
        ('friend_request', 'Dostluq sorğusu'),
        ('friend_accepted', 'Dostluq qəbul edildi'),
        ('friend_rejected', 'Dostluq rədd edildi'),
        ('friend_new_activity', 'Dost yeni aktivitə yaratdı'),
        
        # Activity notifications (for organizers)
        ('activity_join_request', 'Aktivitəyə qoşulma sorğusu'),
        ('activity_participant_joined', 'Yeni iştirakçı qoşuldu'),
        ('activity_participant_left', 'İştirakçı ayrıldı'),
        ('activity_comment', 'Aktivitəyə yeni şərh'),
        
        # Activity notifications (for participants)
        ('activity_update', 'Aktivitə yeniləndi'),
        ('activity_cancelled', 'Aktivitə ləğv edildi'),
        ('activity_reminder', 'Aktivitə xatırlatması'),
        ('activity_starting_soon', 'Aktivitə tezliklə başlayır'),
        
        # Discovery notifications
        ('new_activity_nearby', 'Yaxınlıqda yeni aktivitə'),
        ('new_activity_interest', 'Maraqlarınıza uyğun aktivitə'),
        
        # Message notifications
        ('new_message', 'Yeni mesaj'),
        
        # System notifications
        ('system', 'Sistem bildirişi'),
        ('promotional', 'Reklam'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects (optional)
    related_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='triggered_notifications')
    related_activity_id = models.IntegerField(null=True, blank=True)
    related_friendship_id = models.IntegerField(null=True, blank=True)
    
    # Notification data (for deep linking)
    data = models.JSONField(default=dict, blank=True, help_text="Additional data for the notification")
    
    # Status
    is_read = models.BooleanField(default=False)
    is_pushed = models.BooleanField(default=False, help_text="Was push notification sent")
    pushed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_notification_type_display()}"
    
    def mark_as_read(self):
        self.is_read = True
        self.save(update_fields=['is_read'])


# Signal to create NotificationSettings when a new User is created
@receiver(post_save, sender=User)
def create_notification_settings(sender, instance, created, **kwargs):
    """Create NotificationSettings for new users"""
    if created:
        NotificationSettings.objects.get_or_create(user=instance)
