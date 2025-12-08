from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from activities.models import Activity
from .models import (
    Language, Interest, InterestCategory, UserImage, OTPVerification, 
    Friendship, BlogPost, BlogCategory, NotificationSettings, PushToken, Notification,
    Conversation, DirectMessage, ActivityGroupChat, ActivityGroupMessage
)
from .serializers import (
    LanguageSerializer, InterestSerializer, InterestCategorySerializer, UserSerializer, UserPublicSerializer,
    UserImageSerializer, OTPSendSerializer, OTPVerifySerializer,
    UserRegistrationSerializer, FriendshipSerializer, BlogPostSerializer, BlogCategorySerializer,
    NotificationSettingsSerializer, PushTokenSerializer, NotificationSerializer,
    ConversationSerializer, DirectMessageSerializer
)

User = get_user_model()


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for languages"""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        # Order languages: Azerbaijan, Turkish, Russian, English first, then others alphabetically
        from django.db.models import Case, When, Value, IntegerField
        priority_codes = ['az', 'tr', 'ru', 'en']
        
        return Language.objects.annotate(
            priority=Case(
                When(code='az', then=Value(0)),
                When(code='tr', then=Value(1)),
                When(code='ru', then=Value(2)),
                When(code='en', then=Value(3)),
                default=Value(100),
                output_field=IntegerField(),
            )
        ).order_by('priority', 'name')


class InterestViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for interests"""
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Interest.objects.all()
        category = self.request.query_params.get('category', None)
        is_general = self.request.query_params.get('is_general', None)
        
        if category:
            queryset = queryset.filter(category=category)
        if is_general == 'true':
            queryset = queryset.filter(is_general=True)
        
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def grouped(self, request):
        """Get interests grouped by category"""
        categories = InterestCategory.objects.filter(is_active=True).prefetch_related('interests').order_by('order', 'name')
        
        grouped_data = []
        for category in categories:
            interests = category.interests.all().order_by('name')
            if interests.exists():
                grouped_data.append({
                    'category': InterestCategorySerializer(category).data,
                    'interests': InterestSerializer(interests, many=True, context={'request': request}).data
                })
        
        return Response(grouped_data)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for users"""
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return UserPublicSerializer
        return UserSerializer
    
    def get_queryset(self):
        if self.action == 'me' or self.action == 'update' or self.action == 'partial_update':
            return User.objects.filter(id=self.request.user.id).prefetch_related('languages', 'interests', 'images')
        return User.objects.all().prefetch_related('languages', 'interests', 'images')
    
    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get or update current user profile"""
        if request.method == 'GET':
            serializer = UserSerializer(request.user, context={'request': request})
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            serializer = UserSerializer(
                request.user, 
                data=request.data, 
                partial=request.method == 'PATCH',
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            # Log validation errors for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Profile update validation errors: {serializer.errors}')
            logger.error(f'Request data: {request.data}')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def send_otp(self, request):
        """Send OTP to phone number"""
        serializer = OTPSendSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            purpose = serializer.validated_data['purpose']
            
            # Generate OTP (in production, use proper SMS service)
            import random
            otp_code = str(random.randint(100000, 999999))
            
            # Create or update OTP verification
            otp_verification, created = OTPVerification.objects.get_or_create(
                phone=phone,
                purpose=purpose,
                defaults={'otp_code': otp_code, 'is_verified': False}
            )
            
            if not created:
                otp_verification.otp_code = otp_code
                otp_verification.is_verified = False
                otp_verification.attempts = 0
                otp_verification.save()
            
            # TODO: Send SMS via service like Twilio, AWS SNS, etc.
            # For now, return OTP in response (remove in production!)
            return Response({
                'success': True,
                'message': 'OTP sent successfully',
                'otp_code': otp_code  # Remove this in production!
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def verify_otp(self, request):
        """Verify OTP code"""
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone']
            otp_code = serializer.validated_data['otp_code']
            purpose = serializer.validated_data['purpose']
            
            try:
                otp_verification = OTPVerification.objects.filter(
                    phone=phone,
                    purpose=purpose,
                    is_verified=False
                ).latest('created_at')
                
                if otp_verification.otp_code == otp_code:
                    otp_verification.is_verified = True
                    otp_verification.save()
                    
                    # If login purpose, authenticate user
                    if purpose == 'login':
                        try:
                            user = User.objects.get(phone=phone)
                            token, created = Token.objects.get_or_create(user=user)
                            return Response({
                                'success': True,
                                'message': 'OTP verified successfully',
                                'token': token.key,
                                'user': UserSerializer(user, context={'request': request}).data
                            })
                        except User.DoesNotExist:
                            return Response({
                                'success': False,
                                'message': 'User not found. Please register first.'
                            }, status=status.HTTP_404_NOT_FOUND)
                    
                    return Response({
                        'success': True,
                        'message': 'OTP verified successfully'
                    })
                else:
                    otp_verification.attempts += 1
                    otp_verification.save()
                    return Response({
                        'success': False,
                        'message': 'Invalid OTP code'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except OTPVerification.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'OTP not found or already verified'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Register new user"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_phone_verified = True
            user.registration_step = 1  # After phone and password registration
            user.save()
            
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'success': True,
                'message': 'User registered successfully',
                'token': token.key,
                'user': UserSerializer(user, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Registration failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """Login with phone and password"""
        phone = request.data.get('phone')
        password = request.data.get('password')
        
        # Remove spaces from phone number
        if phone:
            phone = phone.replace(' ', '')
        
        if not phone or not password:
            return Response({
                'success': False,
                'message': 'Phone and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get user directly by phone (same as web version)
            user = User.objects.get(phone=phone)
            
            # Check password
            if user.check_password(password):
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'success': True,
                    'message': 'Login successful',
                    'token': token.key,
                    'user': UserSerializer(user, context={'request': request}).data
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Invalid phone or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid phone or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def google_auth(self, request):
        """
        Authenticate or register with Google.
        Accepts Google ID token and user info from mobile app.
        """
        google_id = request.data.get('google_id')
        email = request.data.get('email')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '') or '.'
        
        if not google_id or not email:
            return Response({
                'success': False,
                'message': 'Google ID and email are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Check if user exists with this email
            user = User.objects.get(email=email)
            is_new_user = False
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create(
                phone=f'+000{google_id[:12]}',  # Placeholder phone
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_google_signup=True,
                is_phone_verified=True,
                registration_step=2,  # Skip phone step
                is_registration_complete=False,
            )
            user.set_unusable_password()
            user.save()
            is_new_user = True
        
        # Create or get token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'success': True,
            'message': 'Google authentication successful',
            'token': token.key,
            'user': UserSerializer(user, context={'request': request}).data,
            'is_new_user': is_new_user,
            'needs_registration': not user.is_registration_complete,
            'registration_step': user.registration_step,
        })
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upload_image(self, request):
        """Upload user profile image"""
        if 'image' not in request.FILES:
            return Response({
                'success': False,
                'message': 'Image file is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image = request.FILES['image']
        is_primary = request.data.get('is_primary', False)
        
        user_image = UserImage.objects.create(
            user=request.user,
            image=image,
            is_primary=is_primary
        )
        
        serializer = UserImageSerializer(user_image, context={'request': request})
        return Response({
            'success': True,
            'image': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def friends(self, request, pk=None):
        """Get user's friends"""
        user = self.get_object()
        friends = Friendship.get_friends(user)
        serializer = UserPublicSerializer(friends, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='my-friends', permission_classes=[permissions.IsAuthenticated])
    def my_friends(self, request):
        """Get current user's friends"""
        friends = Friendship.get_friends(request.user)
        serializer = UserPublicSerializer(friends, many=True, context={'request': request})
        return Response(serializer.data)


class FriendshipViewSet(viewsets.ModelViewSet):
    """ViewSet for friendships"""
    queryset = Friendship.objects.all()
    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Friendship.objects.filter(
            Q(from_user=user) | Q(to_user=user)
        )
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def send_request(self, request):
        """Send friend request"""
        to_user_id = request.data.get('to_user_id')
        if not to_user_id:
            return Response({
                'success': False,
                'message': 'to_user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            to_user = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if to_user == request.user:
            return Response({
                'success': False,
                'message': 'Cannot send friend request to yourself'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        friendship, created = Friendship.objects.get_or_create(
            from_user=request.user,
            to_user=to_user,
            defaults={'status': 'pending'}
        )
        
        if not created:
            return Response({
                'success': False,
                'message': 'Friend request already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = FriendshipSerializer(friendship, context={'request': request})
        return Response({
            'success': True,
            'friendship': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def accept(self, request, pk=None):
        """Accept friend request"""
        friendship = self.get_object()
        if friendship.to_user != request.user:
            return Response({
                'success': False,
                'message': 'You can only accept requests sent to you'
            }, status=status.HTTP_403_FORBIDDEN)
        
        friendship.status = 'accepted'
        friendship.save()
        
        serializer = FriendshipSerializer(friendship, context={'request': request})
        return Response({
            'success': True,
            'friendship': serializer.data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reject(self, request, pk=None):
        """Reject friend request"""
        friendship = self.get_object()
        if friendship.to_user != request.user:
            return Response({
                'success': False,
                'message': 'You can only reject requests sent to you'
            }, status=status.HTTP_403_FORBIDDEN)
        
        friendship.status = 'rejected'
        friendship.save()
        
        serializer = FriendshipSerializer(friendship, context={'request': request})
        return Response({
            'success': True,
            'friendship': serializer.data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def status(self, request):
        """Get friendship status with another user"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({
                'success': False,
                'message': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if other_user == request.user:
            return Response({
                'success': False,
                'message': 'Cannot check friendship status with yourself'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if friendship exists in either direction
        friendship = Friendship.objects.filter(
            Q(from_user=request.user, to_user=other_user) |
            Q(from_user=other_user, to_user=request.user)
        ).first()
        
        if not friendship:
            return Response({
                'success': True,
                'status': None,
                'friendship': None
            })
        
        serializer = FriendshipSerializer(friendship, context={'request': request})
        return Response({
            'success': True,
            'status': friendship.status,
            'is_sender': friendship.from_user == request.user,
            'friendship_id': friendship.id,
            'friendship': serializer.data
        })


class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for blog categories"""
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [permissions.AllowAny]


class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for blog posts"""
    queryset = BlogPost.objects.filter(is_published=True)
    serializer_class = BlogPostSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True)
        category_slug = self.request.query_params.get('category', None)
        is_featured = self.request.query_params.get('featured', None)
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if is_featured == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset.select_related('author', 'category').order_by('-published_at', '-created_at')


class NotificationSettingsViewSet(viewsets.ViewSet):
    """ViewSet for user notification settings"""
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        """Get current user's notification settings"""
        settings, created = NotificationSettings.objects.get_or_create(user=request.user)
        serializer = NotificationSettingsSerializer(settings)
        return Response(serializer.data)
    
    def partial_update(self, request, pk=None):
        """Update notification settings"""
        settings, created = NotificationSettings.objects.get_or_create(user=request.user)
        serializer = NotificationSettingsSerializer(settings, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Bildiriş ayarları yeniləndi',
                'settings': serializer.data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def toggle_all(self, request):
        """Toggle all notifications on/off"""
        enabled = request.data.get('enabled', True)
        settings, created = NotificationSettings.objects.get_or_create(user=request.user)
        
        # Update all notification settings
        settings.friend_requests = enabled
        settings.friend_request_accepted = enabled
        settings.friend_new_activity = enabled
        settings.activity_join_request = enabled
        settings.activity_participant_left = enabled
        settings.activity_comment = enabled
        settings.activity_update = enabled
        settings.activity_cancelled = enabled
        settings.activity_reminder = enabled
        settings.new_activities_nearby = enabled
        settings.new_activities_interests = enabled
        settings.new_message = enabled
        settings.system_updates = enabled
        settings.push_enabled = enabled
        settings.save()
        
        serializer = NotificationSettingsSerializer(settings)
        return Response({
            'success': True,
            'message': 'Bütün bildirişlər ' + ('aktivləşdirildi' if enabled else 'söndürüldü'),
            'settings': serializer.data
        })


class PushTokenViewSet(viewsets.ViewSet):
    """ViewSet for managing push notification tokens"""
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request):
        """Register or update a push token"""
        token = request.data.get('token')
        platform = request.data.get('platform', 'android')
        device_name = request.data.get('device_name', '')
        
        if not token:
            return Response({
                'success': False,
                'message': 'Token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Deactivate any existing tokens with this value for other users
        PushToken.objects.filter(token=token).exclude(user=request.user).update(is_active=False)
        
        # Get or create the token for this user
        push_token, created = PushToken.objects.update_or_create(
            token=token,
            defaults={
                'user': request.user,
                'platform': platform,
                'device_name': device_name,
                'is_active': True
            }
        )
        
        serializer = PushTokenSerializer(push_token)
        return Response({
            'success': True,
            'message': 'Push token registered' if created else 'Push token updated',
            'token': serializer.data
        })
    
    def destroy(self, request, pk=None):
        """Deactivate a push token (on logout)"""
        token = request.data.get('token')
        
        if token:
            PushToken.objects.filter(token=token, user=request.user).update(is_active=False)
        else:
            # Deactivate all tokens for this user
            PushToken.objects.filter(user=request.user).update(is_active=False)
        
        return Response({
            'success': True,
            'message': 'Push token deactivated'
        })
    
    @action(detail=False, methods=['post'])
    def deactivate(self, request):
        """Deactivate a push token by token value"""
        token = request.data.get('token')
        
        if token:
            PushToken.objects.filter(token=token, user=request.user).update(is_active=False)
            return Response({
                'success': True,
                'message': 'Push token deactivated'
            })
        
        return Response({
            'success': False,
            'message': 'Token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def test_notification(self, request):
        """Send a test push notification to the current user"""
        from .push_service import push_service
        
        # Get user's push tokens
        tokens = push_service.get_user_push_tokens(request.user)
        
        if not tokens:
            return Response({
                'success': False,
                'message': 'No push tokens found. Make sure you are logged in on a device.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Send test notification
        title = request.data.get('title', 'Test Bildirişi 🎉')
        body = request.data.get('body', 'Bu test bildirişidir. Push notifications işləyir!')
        
        result = push_service.send_push_notification(
            tokens=tokens,
            title=title,
            body=body,
            data={'screen': 'Notifications', 'test': True}
        )
        
        if result.get('success'):
            return Response({
                'success': True,
                'message': 'Test notification sent successfully',
                'tokens_count': len(tokens),
                'result': result.get('data')
            })
        
        return Response({
            'success': False,
            'message': 'Failed to send notification',
            'error': result.get('error')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user notifications"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({
            'unread_count': count
        })
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save(update_fields=['is_read'])
            return Response({
                'success': True,
                'message': 'Bildiriş oxundu olaraq işarələndi'
            })
        except Notification.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Bildiriş tapılmadı'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        updated = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({
            'success': True,
            'message': f'{updated} bildiriş oxundu olaraq işarələndi'
        })
    
    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """Delete all read notifications"""
        deleted, _ = Notification.objects.filter(user=request.user, is_read=True).delete()
        return Response({
            'success': True,
            'message': f'{deleted} bildiriş silindi'
        })


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for direct message conversations"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.get_user_conversations(self.request.user).order_by('-updated_at')
    
    @action(detail=False, methods=['post'])
    def get_or_create(self, request):
        """Get or create a conversation with another user"""
        other_user_id = request.data.get('user_id')
        
        if not other_user_id:
            return Response({
                'success': False,
                'message': 'user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            other_user = User.objects.get(id=other_user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if other_user == request.user:
            return Response({
                'success': False,
                'message': 'Cannot create conversation with yourself'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if users are friends
        if not Friendship.are_friends(request.user, other_user):
            return Response({
                'success': False,
                'message': 'You can only message friends'
            }, status=status.HTTP_403_FORBIDDEN)
        
        conversation = Conversation.get_or_create_conversation(request.user, other_user)
        serializer = ConversationSerializer(conversation, context={'request': request})
        
        return Response({
            'success': True,
            'conversation': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a conversation"""
        try:
            conversation = self.get_queryset().get(pk=pk)
        except Conversation.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Conversation not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Mark messages as read
        conversation.messages.filter(is_read=False).exclude(sender=request.user).update(
            is_read=True, 
            status='read'
        )
        
        messages = conversation.messages.order_by('created_at')
        serializer = DirectMessageSerializer(messages, many=True, context={'request': request})
        
        return Response({
            'success': True,
            'messages': serializer.data
        })


class DirectMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for direct messages"""
    serializer_class = DirectMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DirectMessage.objects.filter(
            Q(conversation__participant1=self.request.user) |
            Q(conversation__participant2=self.request.user)
        )
    
    def create(self, request):
        """Send a direct message"""
        conversation_id = request.data.get('conversation_id')
        user_id = request.data.get('user_id')
        message_text = request.data.get('message', '').strip()
        
        if not message_text:
            return Response({
                'success': False,
                'message': 'Message text is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(message_text) > 2000:
            return Response({
                'success': False,
                'message': 'Message is too long (max 2000 characters)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create conversation
        if conversation_id:
            try:
                conversation = Conversation.objects.get(
                    Q(pk=conversation_id) &
                    (Q(participant1=request.user) | Q(participant2=request.user))
                )
            except Conversation.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Conversation not found'
                }, status=status.HTTP_404_NOT_FOUND)
        elif user_id:
            try:
                other_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Check if users are friends
            if not Friendship.are_friends(request.user, other_user):
                return Response({
                    'success': False,
                    'message': 'You can only message friends'
                }, status=status.HTTP_403_FORBIDDEN)
            
            conversation = Conversation.get_or_create_conversation(request.user, other_user)
        else:
            return Response({
                'success': False,
                'message': 'conversation_id or user_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the message
        message = DirectMessage.objects.create(
            conversation=conversation,
            sender=request.user,
            message=message_text
        )
        
        # Update conversation timestamp
        conversation.save()  # This updates updated_at
        
        # Send push notification to the other user
        other_user = conversation.get_other_participant(request.user)
        self._send_message_notification(request.user, other_user, message_text, conversation)
        
        serializer = DirectMessageSerializer(message, context={'request': request})
        return Response({
            'success': True,
            'message': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def _send_message_notification(self, sender, recipient, message_text, conversation):
        """Send push notification for new message"""
        try:
            from .push_service import push_service
            import logging
            logger = logging.getLogger(__name__)
            
            # Check if user has new_message notifications enabled
            settings = NotificationSettings.objects.filter(user=recipient).first()
            if settings and not settings.new_message:
                logger.info(f"Skipping message notification for {recipient.id} - notifications disabled")
                return
            
            tokens = push_service.get_user_push_tokens(recipient)
            logger.info(f"Sending message notification to {recipient.id}, tokens: {len(tokens)}")
            
            if tokens:
                # Truncate message for notification
                preview = message_text[:100] + '...' if len(message_text) > 100 else message_text
                
                result = push_service.send_push_notification(
                    tokens=tokens,
                    title=f'💬 {sender.get_full_name()}',
                    body=preview,
                    data={
                        'screen': 'Chat',
                        'conversationId': conversation.id,
                        'userId': sender.id,
                        'type': 'new_message'
                    },
                    channel_id='messages'
                )
                logger.info(f"Push notification result: {result}")
            else:
                logger.warning(f"No push tokens for user {recipient.id}")
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to send message notification: {e}", exc_info=True)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a message as read"""
        try:
            message = self.get_queryset().get(pk=pk)
            if message.sender != request.user:
                message.mark_as_read()
            return Response({
                'success': True,
                'message': 'Message marked as read'
            })
        except DirectMessage.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Message not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ActivityGroupChatViewSet(viewsets.ModelViewSet):
    """ViewSet for activity group chats"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        from .serializers import ActivityGroupChatSerializer, ActivityGroupMessageSerializer
        if self.action == 'messages' or self.action == 'send_message':
            return ActivityGroupMessageSerializer
        return ActivityGroupChatSerializer
    
    def get_queryset(self):
        """Get group chats where user is a participant"""
        from activities.models import ActivityParticipant
        
        # Get activities where user is organizer
        organizer_activities = list(Activity.objects.filter(
            organizer=self.request.user
        ).values_list('id', flat=True))
        
        # Get activities where user is approved participant
        participant_activities = list(ActivityParticipant.objects.filter(
            user=self.request.user,
            status='approved'
        ).values_list('activity_id', flat=True))
        
        all_activities = set(organizer_activities + participant_activities)
        
        return ActivityGroupChat.objects.filter(activity_id__in=all_activities)
    
    @action(detail=False, methods=['get'], url_path='for-activity/(?P<activity_id>[^/.]+)')
    def for_activity(self, request, activity_id=None):
        """Get or create group chat for a specific activity"""
        try:
            activity = Activity.objects.get(id=activity_id)
        except Activity.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Activity not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user can access this chat
        from activities.models import ActivityParticipant
        is_organizer = activity.organizer == request.user
        is_participant = ActivityParticipant.objects.filter(
            activity=activity,
            user=request.user,
            status='approved'
        ).exists()
        
        if not is_organizer and not is_participant:
            return Response({
                'success': False,
                'message': 'You are not a participant of this activity'
            }, status=status.HTTP_403_FORBIDDEN)
        
        group_chat = ActivityGroupChat.get_or_create_for_activity(activity)
        from .serializers import ActivityGroupChatSerializer
        serializer = ActivityGroupChatSerializer(group_chat, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a group chat"""
        group_chat = self.get_object()
        
        if not group_chat.is_participant(request.user):
            return Response({
                'success': False,
                'message': 'You are not a participant of this chat'
            }, status=status.HTTP_403_FORBIDDEN)
        
        messages = group_chat.messages.select_related('sender').order_by('created_at')
        from .serializers import ActivityGroupMessageSerializer
        serializer = ActivityGroupMessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message to the group chat"""
        group_chat = self.get_object()
        
        if not group_chat.is_participant(request.user):
            return Response({
                'success': False,
                'message': 'You are not a participant of this chat'
            }, status=status.HTTP_403_FORBIDDEN)
        
        message_text = request.data.get('message', '').strip()
        
        if not message_text:
            return Response({
                'success': False,
                'message': 'Message text is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(message_text) > 2000:
            return Response({
                'success': False,
                'message': 'Message is too long (max 2000 characters)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the message
        message = ActivityGroupMessage.objects.create(
            group_chat=group_chat,
            sender=request.user,
            message=message_text
        )
        
        # Update group chat timestamp
        group_chat.save()
        
        # Send push notifications to other participants
        self._send_group_message_notification(request.user, group_chat, message_text)
        
        from .serializers import ActivityGroupMessageSerializer
        serializer = ActivityGroupMessageSerializer(message, context={'request': request})
        return Response({
            'success': True,
            'message': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def _send_group_message_notification(self, sender, group_chat, message_text):
        """Send push notification to all participants except sender"""
        try:
            from .push_service import push_service
            
            participants = group_chat.get_participants().exclude(id=sender.id)
            
            for participant in participants:
                # Check if user has message notifications enabled
                settings = NotificationSettings.objects.filter(user=participant).first()
                if settings and not settings.new_message:
                    continue
                
                tokens = push_service.get_user_push_tokens(participant)
                if tokens:
                    preview = message_text[:100] + '...' if len(message_text) > 100 else message_text
                    
                    push_service.send_push_notification(
                        tokens=tokens,
                        title=f'💬 {group_chat.activity.title}',
                        body=f'{sender.get_full_name()}: {preview}',
                        data={
                            'screen': 'ActivityGroupChat',
                            'activityId': group_chat.activity.id,
                            'groupChatId': group_chat.id,
                            'type': 'group_message'
                        },
                        channel_id='messages'
                    )
        except Exception as e:
            print(f"Failed to send group message notification: {e}")

