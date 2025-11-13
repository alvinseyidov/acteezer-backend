from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Language, Interest, UserImage, OTPVerification, Friendship, BlogPost, BlogCategory

User = get_user_model()


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name', 'code']


class InterestSerializer(serializers.ModelSerializer):
    is_general = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Interest
        fields = ['id', 'name', 'icon', 'category', 'is_general']


class UserImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    is_primary = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = UserImage
        fields = ['id', 'image', 'image_url', 'is_primary', 'order', 'uploaded_at']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class UserSerializer(serializers.ModelSerializer):
    images = UserImageSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    interests = InterestSerializer(many=True, read_only=True)
    language_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Language.objects.all(), source='languages', write_only=True, required=False
    )
    interest_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Interest.objects.all(), source='interests', write_only=True, required=False
    )
    age = serializers.ReadOnlyField()
    full_name = serializers.SerializerMethodField()
    is_phone_verified = serializers.BooleanField(read_only=True)
    is_registration_complete = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'phone', 'first_name', 'last_name', 'full_name', 'email',
            'birthday', 'gender', 'bio', 'city', 'latitude', 'longitude', 'address',
            'languages', 'interests', 'language_ids', 'interest_ids',
            'images', 'age', 'is_phone_verified', 'is_registration_complete',
            'registration_step', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_phone_verified', 'is_registration_complete', 'registration_step', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class UserPublicSerializer(serializers.ModelSerializer):
    """Public user profile serializer (limited fields)"""
    images = UserImageSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)
    interests = InterestSerializer(many=True, read_only=True)
    age = serializers.ReadOnlyField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'bio', 'city',
            'languages', 'interests', 'images', 'age', 'gender'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class OTPSendSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=17)
    purpose = serializers.ChoiceField(choices=['registration', 'login', 'password_reset'], default='registration')


class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=17)
    otp_code = serializers.CharField(max_length=6)
    purpose = serializers.ChoiceField(choices=['registration', 'login', 'password_reset'], default='registration')


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['phone', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class FriendshipSerializer(serializers.ModelSerializer):
    from_user = UserPublicSerializer(read_only=True)
    to_user = UserPublicSerializer(read_only=True)
    
    class Meta:
        model = Friendship
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug', 'description', 'created_at']


class BlogPostSerializer(serializers.ModelSerializer):
    author = UserPublicSerializer(read_only=True)
    category = BlogCategorySerializer(read_only=True)
    featured_image_url = serializers.SerializerMethodField()
    is_published = serializers.BooleanField(read_only=True)
    is_featured = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'author', 'category', 'excerpt', 'content',
            'featured_image', 'featured_image_url', 'is_published', 'is_featured',
            'views_count', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = ['id', 'slug', 'author', 'views_count', 'created_at', 'updated_at', 'published_at']
    
    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return obj.featured_image.url
        return None

