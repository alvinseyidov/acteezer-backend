from django.db import models
from django.urls import reverse
from PIL import Image


class PlaceCategory(models.Model):
    """Model for place categories like Restaurant, Pub, Activity Place, Club, etc."""
    CATEGORY_CHOICES = [
        ('restaurant', 'Restaurant'),
        ('pub', 'Pub'),
        ('club', 'Club'), 
        ('activity', 'Activity Place'),
        ('cafe', 'Cafe'),
        ('bar', 'Bar'),
        ('museum', 'Museum'),
        ('park', 'Park'),
        ('shopping', 'Shopping'),
        ('entertainment', 'Entertainment'),
        ('sports', 'Sports'),
        ('cultural', 'Cultural'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    icon = models.CharField(max_length=50, default='fas fa-map-marker-alt')  # FontAwesome icon class
    color = models.CharField(max_length=7, default='#5DD3BE')  # Hex color for category badge
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Place Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Place(models.Model):
    """Model for places in Baku like restaurants, pubs, activity places, clubs, etc."""
    
    PRICE_RANGE_CHOICES = [
        ('budget', '$ - Budget'),
        ('moderate', '$$ - Moderate'), 
        ('expensive', '$$$ - Expensive'),
        ('luxury', '$$$$ - Luxury'),
    ]
    
    DISTRICT_CHOICES = [
        ('nizami', 'Nizami'),
        ('sabail', 'Sabail'),
        ('yasamal', 'Yasamal'),
        ('binagadi', 'Binagadi'),
        ('khazar', 'Khazar'),
        ('sabunchu', 'Sabunchu'),
        ('surakhani', 'Surakhani'),
        ('khatai', 'Khatai'),
        ('narimanov', 'Narimanov'),
        ('nasimi', 'Nasimi'),
        ('pirallahi', 'Pirallahi'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    category = models.ForeignKey(PlaceCategory, on_delete=models.CASCADE, related_name='places')
    description = models.TextField()
    short_description = models.CharField(max_length=300, help_text="Brief description for cards")
    
    # Location Information
    address = models.CharField(max_length=300)
    district = models.CharField(max_length=20, choices=DISTRICT_CHOICES, default='other')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    instagram = models.CharField(max_length=100, blank=True, help_text="Instagram username without @")
    
    # Business Information
    price_range = models.CharField(max_length=10, choices=PRICE_RANGE_CHOICES, default='moderate')
    opening_hours = models.TextField(help_text="Opening hours information")
    features = models.TextField(blank=True, help_text="Special features, amenities, etc.")
    
    # Media
    main_image = models.ImageField(upload_to='places/images/', blank=True, null=True)
    image_alt = models.CharField(max_length=200, blank=True, help_text="Alt text for main image")
    
    # Rating and Reviews
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, help_text="Average rating out of 5")
    review_count = models.PositiveIntegerField(default=0)
    
    # Status and Metadata
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Show in featured places")
    is_verified = models.BooleanField(default=False, help_text="Verified business")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-rating', 'name']
        indexes = [
            models.Index(fields=['category', 'district']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.category.name}"
    
    def get_absolute_url(self):
        return reverse('places:place_detail', kwargs={'pk': self.pk})
    
    def get_rating_stars(self):
        """Return filled and empty stars for rating display"""
        full_stars = int(self.rating)
        half_star = 1 if self.rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        return {
            'full': range(full_stars),
            'half': half_star,
            'empty': range(empty_stars)
        }
    
    def get_price_display(self):
        """Return price range symbols"""
        price_symbols = {
            'budget': '$',
            'moderate': '$$',
            'expensive': '$$$',
            'luxury': '$$$$'
        }
        return price_symbols.get(self.price_range, '$$')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize image if it exists
        if self.main_image:
            img = Image.open(self.main_image.path)
            if img.height > 600 or img.width > 800:
                img.thumbnail((800, 600))
                img.save(self.main_image.path)


class PlaceImage(models.Model):
    """Additional images for places"""
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='places/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"{self.place.name} - Image {self.id}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize image
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 600 or img.width > 800:
                img.thumbnail((800, 600))
                img.save(self.image.path)


class PlaceReview(models.Model):
    """Reviews for places"""
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=100)
    reviewer_email = models.EmailField(blank=True)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['place', 'reviewer_email']
    
    def __str__(self):
        return f"{self.place.name} - {self.rating} stars by {self.reviewer_name}"


class PlaceFavorite(models.Model):
    """Model for user favorites/liked places"""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='favorite_places')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'place']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} liked {self.place.name}"