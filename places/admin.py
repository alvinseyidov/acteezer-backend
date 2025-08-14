from django.contrib import admin
from django.utils.html import format_html
from .models import PlaceCategory, Place, PlaceImage, PlaceReview


@admin.register(PlaceCategory)
class PlaceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'color_preview', 'icon', 'created_at']
    list_filter = ['category_type', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
            obj.color
        )
    color_preview.short_description = "Color"


class PlaceImageInline(admin.TabularInline):
    model = PlaceImage
    extra = 0
    fields = ['image', 'alt_text', 'is_featured']


class PlaceReviewInline(admin.TabularInline):
    model = PlaceReview
    extra = 0
    readonly_fields = ['created_at']
    fields = ['reviewer_name', 'rating', 'comment', 'is_approved', 'created_at']


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'district', 'rating_display', 'price_range', 
        'is_featured', 'is_verified', 'is_active', 'created_at'
    ]
    list_filter = [
        'category', 'district', 'price_range', 'is_featured', 
        'is_verified', 'is_active', 'created_at'
    ]
    search_fields = ['name', 'description', 'address']
    ordering = ['-is_featured', '-rating', 'name']
    inlines = [PlaceImageInline, PlaceReviewInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description', 'short_description')
        }),
        ('Location', {
            'fields': ('address', 'district', 'latitude', 'longitude')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'website', 'instagram')
        }),
        ('Business Information', {
            'fields': ('price_range', 'opening_hours', 'features')
        }),
        ('Media', {
            'fields': ('main_image', 'image_alt')
        }),
        ('Rating & Status', {
            'fields': ('rating', 'review_count', 'is_active', 'is_featured', 'is_verified')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def rating_display(self, obj):
        stars = '★' * int(obj.rating) + '☆' * (5 - int(obj.rating))
        return format_html(
            '<span title="{}/5 ({} reviews)">{}</span>',
            obj.rating, obj.review_count, stars
        )
    rating_display.short_description = "Rating"
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Update review count and average rating
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            obj.review_count = reviews.count()
            obj.rating = sum(review.rating for review in reviews) / reviews.count()
            obj.save()


@admin.register(PlaceImage)
class PlaceImageAdmin(admin.ModelAdmin):
    list_display = ['place', 'image_preview', 'alt_text', 'is_featured', 'created_at']
    list_filter = ['is_featured', 'created_at', 'place__category']
    search_fields = ['place__name', 'alt_text']
    ordering = ['-created_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(PlaceReview)
class PlaceReviewAdmin(admin.ModelAdmin):
    list_display = ['place', 'reviewer_name', 'rating_display', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at', 'place__category']
    search_fields = ['place__name', 'reviewer_name', 'comment']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def rating_display(self, obj):
        return '★' * obj.rating + '☆' * (5 - obj.rating)
    rating_display.short_description = "Rating"
    
    actions = ['approve_reviews', 'disapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} reviews approved.")
    approve_reviews.short_description = "Approve selected reviews"
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"{queryset.count()} reviews disapproved.")
    disapprove_reviews.short_description = "Disapprove selected reviews"