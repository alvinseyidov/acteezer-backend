from rest_framework import serializers
from .models import PlaceCategory, Place, PlaceImage, PlaceReview, PlaceFavorite
from accounts.serializers import UserPublicSerializer


class PlaceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceCategory
        fields = ['id', 'name', 'category_type', 'icon', 'color', 'description', 'created_at']


class PlaceImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    is_featured = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PlaceImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'is_featured', 'created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class PlaceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for place lists"""
    category = PlaceCategorySerializer(read_only=True)
    main_image_url = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()
    is_featured = serializers.BooleanField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Place
        fields = [
            'id', 'name', 'short_description', 'category', 'address', 'district',
            'latitude', 'longitude', 'price_range', 'price_display', 'rating',
            'review_count', 'main_image', 'main_image_url', 'is_featured',
            'is_verified', 'created_at'
        ]
    
    def get_main_image_url(self, obj):
        if obj.main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        return None
    
    def get_price_display(self, obj):
        return obj.get_price_display()


class PlaceDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for place detail view"""
    category = PlaceCategorySerializer(read_only=True)
    images = PlaceImageSerializer(many=True, read_only=True)
    main_image_url = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)
    is_featured = serializers.BooleanField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Place
        fields = [
            'id', 'name', 'short_description', 'description', 'category',
            'address', 'district', 'latitude', 'longitude', 'phone', 'email',
            'website', 'instagram', 'price_range', 'price_display', 'opening_hours',
            'features', 'main_image', 'main_image_url', 'images', 'rating',
            'review_count', 'is_active', 'is_featured', 'is_verified',
            'created_at', 'updated_at'
        ]
    
    def get_main_image_url(self, obj):
        if obj.main_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        return None
    
    def get_price_display(self, obj):
        return obj.get_price_display()


class PlaceReviewSerializer(serializers.ModelSerializer):
    is_approved = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = PlaceReview
        fields = [
            'id', 'place', 'reviewer_name', 'reviewer_email', 'rating',
            'comment', 'is_approved', 'created_at'
        ]
        read_only_fields = ['id', 'is_approved', 'created_at']


class PlaceFavoriteSerializer(serializers.ModelSerializer):
    place = PlaceListSerializer(read_only=True)
    
    class Meta:
        model = PlaceFavorite
        fields = ['id', 'place', 'created_at']
        read_only_fields = ['id', 'created_at']

