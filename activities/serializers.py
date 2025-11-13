from rest_framework import serializers
from .models import (
    ActivityCategory, Activity, ActivityParticipant, 
    ActivityImage, ActivityReview, ActivityComment, ActivityMessage
)
from accounts.serializers import UserPublicSerializer


class ActivityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityCategory
        fields = ['id', 'name', 'category_type', 'icon', 'color', 'description', 'created_at']


class ActivityImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    is_featured = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ActivityImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'is_featured', 'created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ActivityListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for activity lists"""
    category = ActivityCategorySerializer(read_only=True)
    organizer = UserPublicSerializer(read_only=True)
    main_image_url = serializers.SerializerMethodField()
    participants_count = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    is_free = serializers.BooleanField(read_only=True)
    is_featured = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Activity
        fields = [
            'id', 'title', 'short_description', 'category', 'organizer',
            'start_date', 'end_date', 'duration_hours', 'location_name', 'address',
            'district', 'latitude', 'longitude', 'max_participants', 'min_participants',
            'price', 'is_free', 'difficulty_level', 'main_image', 'main_image_url',
            'status', 'is_featured', 'participants_count', 'available_spots',
            'is_upcoming', 'is_ongoing', 'is_past', 'created_at'
        ]
    
    def get_main_image_url(self, obj):
        if obj.main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        return None


class ActivityDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for activity detail view"""
    category = ActivityCategorySerializer(read_only=True)
    organizer = UserPublicSerializer(read_only=True)
    images = ActivityImageSerializer(many=True, read_only=True)
    main_image_url = serializers.SerializerMethodField()
    participants_count = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    pending_requests_count = serializers.ReadOnlyField()
    is_free = serializers.BooleanField(read_only=True)
    is_featured = serializers.BooleanField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Activity
        fields = [
            'id', 'title', 'short_description', 'description', 'category', 'organizer',
            'start_date', 'end_date', 'duration_hours', 'location_name', 'address',
            'district', 'latitude', 'longitude', 'max_participants', 'min_participants',
            'price', 'is_free', 'difficulty_level', 'requirements', 'what_included',
            'min_age', 'max_age', 'allowed_genders', 'main_image', 'main_image_url',
            'images', 'status', 'is_featured', 'contact_phone', 'contact_email',
            'participants_count', 'available_spots', 'pending_requests_count',
            'is_upcoming', 'is_ongoing', 'is_past', 'is_full', 'created_at', 'updated_at'
        ]
    
    def get_main_image_url(self, obj):
        if obj.main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        return None


class ActivityParticipantSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = ActivityParticipant
        fields = [
            'id', 'activity', 'user', 'status', 'message', 'organizer_response',
            'join_requested_at', 'status_updated_at'
        ]
        read_only_fields = ['id', 'join_requested_at', 'status_updated_at']


class ActivityReviewSerializer(serializers.ModelSerializer):
    reviewer = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = ActivityReview
        fields = ['id', 'activity', 'reviewer', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ActivityCommentSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = ActivityComment
        fields = ['id', 'activity', 'user', 'comment', 'parent', 'replies', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        replies = obj.replies.all()
        return ActivityCommentSerializer(replies, many=True, context=self.context).data


class ActivityMessageSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    is_edited = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ActivityMessage
        fields = ['id', 'activity', 'user', 'message', 'created_at', 'updated_at', 'is_edited']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_edited']

