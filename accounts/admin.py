from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User, UserImage, Language, Interest, InterestCategory, OTPVerification, 
    BlogCategory, BlogPost, BlogTag, BlogPostTag, Newsletter, Friendship,
    NotificationSettings, PushToken, Notification
)


class UserImageInline(admin.TabularInline):
    model = UserImage
    extra = 0
    readonly_fields = ['uploaded_at', 'image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 100px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserImageInline]
    
    # List display
    list_display = ['phone', 'first_name', 'last_name', 'gender', 'city', 'is_registration_complete', 'registration_step', 'is_phone_verified', 'created_at']
    list_filter = ['is_registration_complete', 'registration_step', 'is_phone_verified', 'is_staff', 'is_active', 'gender', 'created_at']
    search_fields = ['phone', 'first_name', 'last_name', 'email', 'city']
    ordering = ['-created_at']
    
    # Form organization
    fieldsets = (
        ('Authentication', {
            'fields': ('phone', 'password', 'is_phone_verified')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'gender', 'birthday', 'bio')
        }),
        ('Location', {
            'fields': ('city', 'address', 'latitude', 'longitude')
        }),
        ('Preferences', {
            'fields': ('languages', 'interests')
        }),
        ('Registration Progress', {
            'fields': ('registration_step', 'is_registration_complete')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ['collapse']
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'first_name', 'last_name', 'gender', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    filter_horizontal = ['languages', 'interests', 'groups', 'user_permissions']


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']
    ordering = ['name']


@admin.register(InterestCategory)
class InterestCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'icon', 'order', 'is_active', 'interest_count']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'code']
    prepopulated_fields = {'code': ('name',)}
    ordering = ['order', 'name']
    
    def interest_count(self, obj):
        return obj.interests.count()
    interest_count.short_description = 'Interests'


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'icon', 'is_general']
    list_filter = ['category', 'is_general']
    search_fields = ['name']
    ordering = ['category__order', 'name']


@admin.register(UserImage)
class UserImageAdmin(admin.ModelAdmin):
    list_display = ['user', 'order', 'is_primary', 'uploaded_at', 'image_preview']
    list_filter = ['is_primary', 'uploaded_at']
    search_fields = ['user__phone', 'user__first_name', 'user__last_name']
    ordering = ['user', 'order']
    readonly_fields = ['uploaded_at', 'image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['phone', 'otp_code', 'is_verified', 'attempts', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['phone']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


# Blog Admin Classes
class BlogPostTagInline(admin.TabularInline):
    model = BlogPostTag
    extra = 1


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    inlines = [BlogPostTagInline]
    list_display = ['title', 'author', 'category', 'is_published', 'is_featured', 'views_count', 'published_at']
    list_filter = ['is_published', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    ordering = ['-published_at', '-created_at']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
        ('Statistics', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'user', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'user__first_name', 'user__last_name', 'user__phone']
    ordering = ['-subscribed_at']
    readonly_fields = ['subscribed_at']
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} subscriptions activated.")
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} subscriptions deactivated.")
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at', 'updated_at']
    search_fields = ['from_user__first_name', 'from_user__last_name', 'from_user__phone', 
                     'to_user__first_name', 'to_user__last_name', 'to_user__phone']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Friendship Details', {
            'fields': ('from_user', 'to_user', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('from_user', 'to_user')
    
    actions = ['accept_friendships', 'reject_friendships']
    
    def accept_friendships(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='accepted')
        self.message_user(request, f"{updated} friendship requests accepted.")
    accept_friendships.short_description = "Accept selected pending friendship requests"
    
    def reject_friendships(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='rejected')
        self.message_user(request, f"{updated} friendship requests rejected.")
    reject_friendships.short_description = "Reject selected pending friendship requests"


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'push_enabled', 'email_enabled', 'quiet_hours_enabled', 'updated_at']
    list_filter = ['push_enabled', 'email_enabled', 'quiet_hours_enabled']
    search_fields = ['user__phone', 'user__first_name', 'user__last_name']
    ordering = ['-updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Friend Notifications', {
            'fields': ('friend_requests', 'friend_request_accepted', 'friend_new_activity')
        }),
        ('Activity Notifications (Organizer)', {
            'fields': ('activity_join_request', 'activity_participant_left', 'activity_comment')
        }),
        ('Activity Notifications (Participant)', {
            'fields': ('activity_update', 'activity_cancelled', 'activity_reminder')
        }),
        ('Discovery Notifications', {
            'fields': ('new_activities_nearby', 'new_activities_interests')
        }),
        ('Message Notifications', {
            'fields': ('new_message',)
        }),
        ('System Notifications', {
            'fields': ('system_updates', 'promotional')
        }),
        ('Delivery Preferences', {
            'fields': ('push_enabled', 'email_enabled')
        }),
        ('Quiet Hours', {
            'fields': ('quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(PushToken)
class PushTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'device_name', 'is_active', 'created_at']
    list_filter = ['platform', 'is_active', 'created_at']
    search_fields = ['user__phone', 'user__first_name', 'user__last_name', 'token', 'device_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Token Details', {
            'fields': ('user', 'token', 'platform', 'device_name', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'is_pushed', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_pushed', 'created_at']
    search_fields = ['user__phone', 'user__first_name', 'user__last_name', 'title', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'pushed_at']
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('Related Objects', {
            'fields': ('related_user', 'related_activity_id', 'related_friendship_id', 'data'),
            'classes': ['collapse']
        }),
        ('Status', {
            'fields': ('is_read', 'is_pushed', 'pushed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ['collapse']
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} notifications marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} notifications marked as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"
