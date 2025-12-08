from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Language, Interest, InterestCategory, UserImage, OTPVerification, 
    Friendship, BlogPost, BlogCategory, NotificationSettings, PushToken, Notification,
    Conversation, DirectMessage
)

User = get_user_model()


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name', 'code']


class InterestCategorySerializer(serializers.ModelSerializer):
    emoji_icon = serializers.SerializerMethodField()
    
    class Meta:
        model = InterestCategory
        fields = ['id', 'name', 'code', 'icon', 'emoji_icon', 'order']
    
    def get_emoji_icon(self, obj):
        """Map Font Awesome icons to emoji for mobile app"""
        icon_mapping = {
            'fas fa-running': '🏃',
            'fas fa-futbol': '⚽',
            'fas fa-basketball-ball': '🏀',
            'fas fa-dumbbell': '💪',
            'fas fa-swimming-pool': '🏊',
            'fas fa-bicycle': '🚴',
            'fas fa-hiking': '🥾',
            'fas fa-music': '🎵',
            'fas fa-guitar': '🎸',
            'fas fa-headphones': '🎧',
            'fas fa-paint-brush': '🎨',
            'fas fa-palette': '🎨',
            'fas fa-camera': '📷',
            'fas fa-film': '🎬',
            'fas fa-theater-masks': '🎭',
            'fas fa-book': '📚',
            'fas fa-graduation-cap': '🎓',
            'fas fa-laptop': '💻',
            'fas fa-code': '👨‍💻',
            'fas fa-gamepad': '🎮',
            'fas fa-utensils': '🍽️',
            'fas fa-coffee': '☕',
            'fas fa-wine-glass': '🍷',
            'fas fa-cocktail': '🍸',
            'fas fa-plane': '✈️',
            'fas fa-mountain': '⛰️',
            'fas fa-tree': '🌲',
            'fas fa-leaf': '🍃',
            'fas fa-sun': '☀️',
            'fas fa-umbrella-beach': '🏖️',
            'fas fa-car': '🚗',
            'fas fa-motorcycle': '🏍️',
            'fas fa-heart': '❤️',
            'fas fa-users': '👥',
            'fas fa-user-friends': '👫',
            'fas fa-comments': '💬',
            'fas fa-globe': '🌍',
            'fas fa-language': '🗣️',
            'fas fa-pray': '🙏',
            'fas fa-om': '🕉️',
            'fas fa-paw': '🐾',
            'fas fa-dog': '🐕',
            'fas fa-cat': '🐱',
            'fas fa-horse': '🐴',
            'fas fa-briefcase': '💼',
            'fas fa-chart-line': '📈',
            'fas fa-coins': '💰',
            'fas fa-shopping-bag': '🛍️',
            'fas fa-tshirt': '👕',
            'fas fa-gem': '💎',
            'fas fa-spa': '🧘',
            'fas fa-heartbeat': '💓',
            'fas fa-brain': '🧠',
            'fas fa-chess': '♟️',
            'fas fa-dice': '🎲',
            'fas fa-puzzle-piece': '🧩',
            'fas fa-star': '⭐',
            'fas fa-fire': '🔥',
            'fas fa-bolt': '⚡',
            'fas fa-snowflake': '❄️',
            'fas fa-water': '💧',
        }
        return icon_mapping.get(obj.icon, '📌')


class InterestSerializer(serializers.ModelSerializer):
    is_general = serializers.BooleanField(read_only=True)
    icon_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Interest
        fields = ['id', 'name', 'icon', 'icon_image', 'icon_image_url', 'category', 'is_general']
    
    def get_icon_image_url(self, obj):
        if obj.icon_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icon_image.url)
            return obj.icon_image.url
        return None


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
    is_registration_complete = serializers.BooleanField(required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'phone', 'first_name', 'last_name', 'full_name', 'email',
            'birthday', 'gender', 'bio', 'city', 'latitude', 'longitude', 'address',
            'languages', 'interests', 'language_ids', 'interest_ids',
            'images', 'age', 'is_phone_verified', 'is_registration_complete',
            'registration_step', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_phone_verified', 'registration_step', 'created_at', 'updated_at']
    
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
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    
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
        
        # Remove spaces from phone
        phone = validated_data.get('phone', '').replace(' ', '')
        first_name = validated_data.get('first_name', '')
        last_name = validated_data.get('last_name', '')
        
        # Create user using the manager's create_user method
        user = User.objects.create_user(
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
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


class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for user notification settings"""
    
    class Meta:
        model = NotificationSettings
        fields = [
            'id',
            # Friend notifications
            'friend_requests',
            'friend_request_accepted',
            'friend_new_activity',
            # Activity notifications (Organizer)
            'activity_join_request',
            'activity_participant_left',
            'activity_comment',
            # Activity notifications (Participant)
            'activity_update',
            'activity_cancelled',
            'activity_reminder',
            # Discovery notifications
            'new_activities_nearby',
            'new_activities_interests',
            # Message notifications
            'new_message',
            # System notifications
            'system_updates',
            'promotional',
            # Delivery preferences
            'push_enabled',
            'email_enabled',
            # Quiet hours
            'quiet_hours_enabled',
            'quiet_hours_start',
            'quiet_hours_end',
            # Timestamps
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']


class PushTokenSerializer(serializers.ModelSerializer):
    """Serializer for push notification tokens"""
    
    class Meta:
        model = PushToken
        fields = ['id', 'token', 'platform', 'device_name', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications"""
    related_user = UserPublicSerializer(read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'notification_type_display',
            'title',
            'message',
            'related_user',
            'related_activity_id',
            'related_friendship_id',
            'data',
            'is_read',
            'created_at',
        ]
        read_only_fields = ['id', 'notification_type', 'title', 'message', 'related_user', 
                          'related_activity_id', 'related_friendship_id', 'data', 'created_at']


class DirectMessageSerializer(serializers.ModelSerializer):
    """Serializer for direct messages"""
    sender = UserPublicSerializer(read_only=True)
    is_me = serializers.SerializerMethodField()
    
    class Meta:
        model = DirectMessage
        fields = [
            'id', 'conversation', 'sender', 'message', 'status', 
            'is_read', 'read_at', 'created_at', 'is_me'
        ]
        read_only_fields = ['id', 'sender', 'status', 'is_read', 'read_at', 'created_at']
    
    def get_is_me(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.sender == request.user
        return False


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations"""
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'other_user', 'last_message', 'unread_count', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_other_user(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            other = obj.get_other_participant(request.user)
            return UserPublicSerializer(other, context=self.context).data
        return None
    
    def get_last_message(self, obj):
        last_msg = obj.get_last_message()
        if last_msg:
            return {
                'id': last_msg.id,
                'message': last_msg.message,
                'sender_id': last_msg.sender_id,
                'is_read': last_msg.is_read,
                'created_at': last_msg.created_at.isoformat()
            }
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.get_unread_count(request.user)
        return 0


class ActivityGroupMessageSerializer(serializers.ModelSerializer):
    """Serializer for activity group messages"""
    sender = UserPublicSerializer(read_only=True)
    is_me = serializers.SerializerMethodField()
    
    class Meta:
        from .models import ActivityGroupMessage
        model = ActivityGroupMessage
        fields = [
            'id', 'group_chat', 'sender', 'message', 'status', 
            'created_at', 'is_me'
        ]
        read_only_fields = ['id', 'sender', 'status', 'created_at']
    
    def get_is_me(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.sender == request.user
        return False


class ActivityGroupChatSerializer(serializers.ModelSerializer):
    """Serializer for activity group chats"""
    activity_title = serializers.CharField(source='activity.title', read_only=True)
    activity_image = serializers.SerializerMethodField()
    participants_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        from .models import ActivityGroupChat
        model = ActivityGroupChat
        fields = [
            'id', 'activity', 'activity_title', 'activity_image',
            'participants_count', 'last_message', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_activity_image(self, obj):
        if obj.activity.images.exists():
            return obj.activity.images.first().image_url
        return None
    
    def get_participants_count(self, obj):
        return obj.get_participants().count()
    
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'id': last_msg.id,
                'message': last_msg.message,
                'sender_name': last_msg.sender.get_full_name(),
                'sender_id': last_msg.sender_id,
                'created_at': last_msg.created_at.isoformat()
            }
        return None
