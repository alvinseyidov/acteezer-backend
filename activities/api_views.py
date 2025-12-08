from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from .models import (
    ActivityCategory, Activity, ActivityParticipant,
    ActivityImage, ActivityReview, ActivityComment, ActivityMessage
)
from .serializers import (
    ActivityCategorySerializer, ActivityListSerializer, ActivityDetailSerializer,
    ActivityWriteSerializer, ActivityParticipantSerializer, ActivityReviewSerializer,
    ActivityCommentSerializer, ActivityMessageSerializer, LanguageSerializer
)
from accounts.models import Language


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for languages"""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [permissions.AllowAny]


class ActivityCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for activity categories"""
    queryset = ActivityCategory.objects.all()
    serializer_class = ActivityCategorySerializer
    permission_classes = [permissions.AllowAny]


class ActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for activities"""
    queryset = Activity.objects.filter(status='published')
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ActivityDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ActivityWriteSerializer
        return ActivityListSerializer
    
    def get_queryset(self):
        # For authenticated users, show their own activities regardless of status
        if self.request.user.is_authenticated:
            queryset = Activity.objects.filter(
                Q(status='published') | Q(organizer=self.request.user)
            )
        else:
            queryset = Activity.objects.filter(status='published')
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(short_description__icontains=search) |
                Q(location_name__icontains=search) |
                Q(address__icontains=search)
            )
        
        # Category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__category_type=category)
        
        # District filter
        district = self.request.query_params.get('district', None)
        if district:
            queryset = queryset.filter(district=district)
        
        # Date filter
        date_filter = self.request.query_params.get('date', None)
        now = timezone.now()
        if date_filter == 'today':
            queryset = queryset.filter(start_date__date=now.date())
        elif date_filter == 'upcoming':
            queryset = queryset.filter(start_date__gt=now)
        
        # Price filter
        price_filter = self.request.query_params.get('price', None)
        if price_filter == 'free':
            queryset = queryset.filter(is_free=True)
        elif price_filter == 'paid':
            queryset = queryset.filter(is_free=False)
        
        # Difficulty filter
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Sorting
        sort_by = self.request.query_params.get('sort', 'featured')
        if sort_by == 'date':
            queryset = queryset.order_by('start_date')
        elif sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        else:  # featured
            queryset = queryset.order_by('-is_featured', 'start_date')
        
        return queryset.select_related('category', 'organizer').prefetch_related('images')
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, pk=None):
        """Join an activity"""
        activity = self.get_object()
        message = request.data.get('message', '')
        
        can_join, join_message = activity.can_user_join(request.user)
        
        if not can_join:
            return Response({
                'success': False,
                'message': join_message
            }, status=status.HTTP_400_BAD_REQUEST)
        
        participant, created = ActivityParticipant.objects.get_or_create(
            activity=activity,
            user=request.user,
            defaults={'message': message, 'status': 'pending'}
        )
        
        if not created:
            return Response({
                'success': False,
                'message': 'You have already requested to join this activity'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Send push notification to organizer
        self._send_join_request_notification(activity, request.user)
        
        serializer = ActivityParticipantSerializer(participant, context={'request': request})
        return Response({
            'success': True,
            'message': 'Join request sent successfully',
            'participant': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def _send_join_request_notification(self, activity, requester):
        """Send push notification to activity organizer about new join request"""
        try:
            from accounts.push_service import push_service
            from accounts.models import NotificationSettings, Notification
            
            organizer = activity.organizer
            
            # Check if organizer has this notification type enabled
            settings = NotificationSettings.objects.filter(user=organizer).first()
            if settings and not settings.activity_join_request:
                return
            
            # Create notification in database
            Notification.objects.create(
                user=organizer,
                notification_type='activity_join_request',
                title='Yeni qoşulma sorğusu 🙋',
                message=f'{requester.get_full_name()} "{activity.title}" aktivitəsinə qoşulmaq istəyir',
                related_user=requester,
                related_activity_id=activity.id,
                data={'activity_id': activity.id, 'requester_id': requester.id}
            )
            
            # Send push notification
            tokens = push_service.get_user_push_tokens(organizer)
            if tokens:
                push_service.send_push_notification(
                    tokens=tokens,
                    title='Yeni qoşulma sorğusu 🙋',
                    body=f'{requester.get_full_name()} "{activity.title}" aktivitəsinə qoşulmaq istəyir',
                    data={
                        'screen': 'ActivityDetail',
                        'activityId': activity.id,
                        'type': 'activity_join_request'
                    },
                    channel_id='default'
                )
        except Exception as e:
            print(f"Failed to send join request notification: {e}")
    
    def _send_participant_status_notification(self, activity, participant_user, status_type):
        """Send push notification to participant about their request status"""
        try:
            from accounts.push_service import push_service
            from accounts.models import NotificationSettings, Notification
            
            # Determine notification type and message
            if status_type == 'approved':
                notification_type = 'activity_participant_joined'
                title = 'Qoşulma sorğunuz qəbul edildi! 🎉'
                message = f'"{activity.title}" aktivitəsinə qoşuldunuz!'
            else:
                notification_type = 'activity_update'
                title = 'Qoşulma sorğunuz rədd edildi'
                message = f'"{activity.title}" aktivitəsinə qoşulma sorğunuz rədd edildi'
            
            # Create notification in database
            Notification.objects.create(
                user=participant_user,
                notification_type=notification_type,
                title=title,
                message=message,
                related_activity_id=activity.id,
                data={'activity_id': activity.id, 'status': status_type}
            )
            
            # Send push notification
            tokens = push_service.get_user_push_tokens(participant_user)
            if tokens:
                push_service.send_push_notification(
                    tokens=tokens,
                    title=title,
                    body=message,
                    data={
                        'screen': 'ActivityDetail',
                        'activityId': activity.id,
                        'type': notification_type
                    },
                    channel_id='default'
                )
        except Exception as e:
            print(f"Failed to send participant status notification: {e}")
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel_join(self, request, pk=None):
        """Cancel join request"""
        activity = self.get_object()
        
        try:
            participant = ActivityParticipant.objects.get(
                activity=activity,
                user=request.user
            )
            if participant.status in ['pending', 'approved']:
                participant.delete()
                return Response({
                    'success': True,
                    'message': 'Join request cancelled'
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Cannot cancel this request'
                }, status=status.HTTP_400_BAD_REQUEST)
        except ActivityParticipant.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Join request not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def participants(self, request, pk=None):
        """Get activity participants"""
        activity = self.get_object()
        
        # Only organizer can see all participants
        if activity.organizer != request.user:
            participants = activity.participants.filter(status='approved')
        else:
            participants = activity.participants.all()
        
        serializer = ActivityParticipantSerializer(participants, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def manage_participant(self, request, pk=None):
        """Manage participant (approve/reject) - organizer only"""
        activity = self.get_object()
        
        if activity.organizer != request.user:
            return Response({
                'success': False,
                'message': 'Only organizer can manage participants'
            }, status=status.HTTP_403_FORBIDDEN)
        
        participant_id = request.data.get('participant_id')
        action_type = request.data.get('action')  # 'approve' or 'reject'
        response_message = request.data.get('response', '')
        
        try:
            participant = ActivityParticipant.objects.get(
                id=participant_id,
                activity=activity
            )
            
            if action_type == 'approve':
                if activity.is_full:
                    return Response({
                        'success': False,
                        'message': 'Activity is full'
                    }, status=status.HTTP_400_BAD_REQUEST)
                participant.status = 'approved'
                self._send_participant_status_notification(activity, participant.user, 'approved')
            elif action_type == 'reject':
                participant.status = 'rejected'
                self._send_participant_status_notification(activity, participant.user, 'rejected')
            else:
                return Response({
                    'success': False,
                    'message': 'Invalid action'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            participant.organizer_response = response_message
            participant.save()
            
            serializer = ActivityParticipantSerializer(participant, context={'request': request})
            return Response({
                'success': True,
                'participant': serializer.data
            })
        except ActivityParticipant.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Participant not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def can_join(self, request, pk=None):
        """Check if user can join activity"""
        activity = self.get_object()
        can_join, message = activity.can_user_join(request.user)
        
        return Response({
            'can_join': can_join,
            'message': message
        })


class ActivityCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for activity comments"""
    queryset = ActivityComment.objects.all()
    serializer_class = ActivityCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        activity_id = self.request.query_params.get('activity', None)
        if activity_id:
            return ActivityComment.objects.filter(activity_id=activity_id, parent=None)
        return ActivityComment.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ActivityMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for activity chat messages"""
    queryset = ActivityMessage.objects.all()
    serializer_class = ActivityMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        activity_id = self.request.query_params.get('activity', None)
        if activity_id:
            # Check if user is participant or organizer
            try:
                activity = Activity.objects.get(id=activity_id)
                if activity.organizer == self.request.user:
                    return ActivityMessage.objects.filter(activity_id=activity_id)
                
                # Check if user is approved participant
                is_participant = ActivityParticipant.objects.filter(
                    activity=activity,
                    user=self.request.user,
                    status='approved'
                ).exists()
                
                if is_participant:
                    return ActivityMessage.objects.filter(activity_id=activity_id)
            except Activity.DoesNotExist:
                pass
        
        return ActivityMessage.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

