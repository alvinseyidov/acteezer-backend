from django.contrib import admin
from django.utils.html import format_html
from .models import ActivityCategory, Activity, ActivityParticipant, ActivityImage, ActivityReview, ActivityComment, ActivityMessage


@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
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


class ActivityImageInline(admin.TabularInline):
    model = ActivityImage
    extra = 0
    fields = ['image', 'alt_text', 'is_featured']


class ActivityParticipantInline(admin.TabularInline):
    model = ActivityParticipant
    extra = 0
    readonly_fields = ['join_requested_at', 'status_updated_at']
    fields = ['user', 'status', 'message', 'organizer_response', 'join_requested_at']


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'organizer', 'start_date', 'status', 
        'participants_info', 'is_featured', 'created_at'
    ]
    list_filter = [
        'category', 'status', 'district', 'difficulty_level', 
        'is_featured', 'is_free', 'start_date', 'created_at'
    ]
    search_fields = ['title', 'description', 'organizer__first_name', 'organizer__last_name', 'location_name']
    ordering = ['-is_featured', 'start_date']
    inlines = [ActivityImageInline, ActivityParticipantInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'category', 'description', 'short_description', 'organizer')
        }),
        ('Date & Time', {
            'fields': ('start_date', 'end_date', 'duration_hours')
        }),
        ('Location', {
            'fields': ('location_name', 'address', 'district', 'latitude', 'longitude')
        }),
        ('Capacity & Pricing', {
            'fields': ('max_participants', 'min_participants', 'price', 'is_free')
        }),
        ('Activity Details', {
            'fields': ('difficulty_level', 'requirements', 'what_included')
        }),
        ('Participant Requirements', {
            'fields': ('required_languages', 'allowed_genders', 'min_age', 'max_age')
        }),
        ('Media', {
            'fields': ('main_image', 'image_alt')
        }),
        ('Contact & Status', {
            'fields': ('contact_phone', 'contact_email', 'status', 'is_featured')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['required_languages']
    
    def participants_info(self, obj):
        approved = obj.participants.filter(status='approved').count()
        pending = obj.participants.filter(status='pending').count()
        return format_html(
            '<span style="color: green;">{}</span>/<span style="color: orange;">{}</span>/<span style="color: blue;">{}</span>',
            approved, pending, obj.max_participants
        )
    participants_info.short_description = "Participants (Approved/Pending/Max)"


@admin.register(ActivityParticipant)
class ActivityParticipantAdmin(admin.ModelAdmin):
    list_display = ['activity', 'user', 'status_badge', 'join_requested_at']
    list_filter = ['status', 'join_requested_at', 'activity__category']
    search_fields = ['activity__title', 'user__first_name', 'user__last_name', 'user__email']
    ordering = ['-join_requested_at']
    readonly_fields = ['join_requested_at', 'status_updated_at']
    
    def status_badge(self, obj):
        badge_class = obj.get_status_badge_class()
        return format_html(
            '<span class="badge {}">{}</span>',
            badge_class, obj.get_status_display()
        )
    status_badge.short_description = "Status"
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} requests approved.")
    approve_requests.short_description = "Approve selected requests"
    
    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} requests rejected.")
    reject_requests.short_description = "Reject selected requests"


@admin.register(ActivityImage)
class ActivityImageAdmin(admin.ModelAdmin):
    list_display = ['activity', 'image_preview', 'alt_text', 'is_featured', 'created_at']
    list_filter = ['is_featured', 'created_at', 'activity__category']
    search_fields = ['activity__title', 'alt_text']
    ordering = ['-created_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(ActivityReview)
class ActivityReviewAdmin(admin.ModelAdmin):
    list_display = ['activity', 'reviewer', 'rating_display', 'created_at']
    list_filter = ['rating', 'created_at', 'activity__category']
    search_fields = ['activity__title', 'reviewer__first_name', 'reviewer__last_name', 'comment']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def rating_display(self, obj):
        return '★' * obj.rating + '☆' * (5 - obj.rating)
    rating_display.short_description = "Rating"


@admin.register(ActivityComment)
class ActivityCommentAdmin(admin.ModelAdmin):
    list_display = ['activity', 'user', 'comment_preview', 'is_reply', 'created_at']
    list_filter = ['created_at', 'activity__category']
    search_fields = ['activity__title', 'user__first_name', 'user__last_name', 'comment']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def comment_preview(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = "Comment"


@admin.register(ActivityMessage)
class ActivityMessageAdmin(admin.ModelAdmin):
    list_display = ['activity', 'user', 'message_preview', 'is_edited', 'created_at']
    list_filter = ['is_edited', 'created_at', 'activity__category']
    search_fields = ['activity__title', 'user__first_name', 'user__last_name', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def message_preview(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    message_preview.short_description = "Message"