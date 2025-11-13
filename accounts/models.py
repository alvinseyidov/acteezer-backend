from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
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


class Interest(models.Model):
    """Model for user interests"""
    CATEGORY_CHOICES = [
        ('general', 'General/Popular'),
        ('beauty', 'Beauty & Fashion'),
        ('lifestyle', 'Lifestyle & Home'),
        ('sports', 'Sports & Fitness'),
        ('arts', 'Arts & Culture'),
        ('food', 'Food & Dining'),
        ('travel', 'Travel & Adventure'),
        ('tech', 'Technology'),
        ('music', 'Music'),
        ('nature', 'Nature & Outdoors'),
        ('education', 'Education & Learning'),
        ('health', 'Health & Wellness'),
        ('social', 'Social & Volunteering'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, null=True)  # Font awesome icon name
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
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
