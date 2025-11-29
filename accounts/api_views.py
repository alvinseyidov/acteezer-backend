from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from .models import Language, Interest, InterestCategory, UserImage, OTPVerification, Friendship, BlogPost, BlogCategory
from .serializers import (
    LanguageSerializer, InterestSerializer, InterestCategorySerializer, UserSerializer, UserPublicSerializer,
    UserImageSerializer, OTPSendSerializer, OTPVerifySerializer,
    UserRegistrationSerializer, FriendshipSerializer, BlogPostSerializer, BlogCategorySerializer
)

User = get_user_model()


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for languages"""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [permissions.AllowAny]


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

