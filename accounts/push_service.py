"""
Push Notification Service for Acteezer

This service handles sending push notifications via Expo's push notification service.
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from django.conf import settings
from django.utils import timezone

from .models import User, PushToken, Notification, NotificationSettings

logger = logging.getLogger(__name__)

# Expo Push Notification API endpoint
EXPO_PUSH_URL = 'https://exp.host/--/api/v2/push/send'


class PushNotificationService:
    """Service to send push notifications via Expo"""

    @staticmethod
    def get_user_push_tokens(user: User) -> List[str]:
        """Get all active push tokens for a user"""
        return list(
            PushToken.objects.filter(
                user=user, 
                is_active=True
            ).values_list('token', flat=True)
        )

    @staticmethod
    def get_notification_settings(user: User) -> Optional[NotificationSettings]:
        """Get user's notification settings"""
        try:
            return user.notification_settings
        except NotificationSettings.DoesNotExist:
            # Create default settings if they don't exist
            return NotificationSettings.objects.create(user=user)

    @staticmethod
    def should_send_notification(user: User, notification_type: str) -> bool:
        """Check if user should receive this type of notification"""
        settings = PushNotificationService.get_notification_settings(user)
        
        if not settings or not settings.push_enabled:
            return False
        
        # Check quiet hours
        if settings.quiet_hours_enabled:
            now = timezone.localtime().time()
            start = settings.quiet_hours_start
            end = settings.quiet_hours_end
            
            if start and end:
                if start < end:
                    # Normal case: e.g., 22:00 - 08:00
                    if start <= now <= end:
                        return False
                else:
                    # Overnight case: e.g., 22:00 - 08:00 (next day)
                    if now >= start or now <= end:
                        return False
        
        # Map notification types to settings fields
        notification_type_map = {
            'friend_request': 'friend_requests',
            'friend_accepted': 'friend_request_accepted',
            'friend_rejected': 'friend_request_accepted',
            'friend_new_activity': 'friend_new_activity',
            'activity_join_request': 'activity_join_request',
            'activity_participant_joined': 'activity_join_request',
            'activity_participant_left': 'activity_participant_left',
            'activity_comment': 'activity_comment',
            'activity_update': 'activity_update',
            'activity_cancelled': 'activity_cancelled',
            'activity_reminder': 'activity_reminder',
            'activity_starting_soon': 'activity_reminder',
            'new_activity_nearby': 'new_activities_nearby',
            'new_activity_interest': 'new_activities_interests',
            'new_message': 'new_message',
            'system': 'system_updates',
            'promotional': 'promotional',
        }
        
        settings_field = notification_type_map.get(notification_type)
        if settings_field:
            return getattr(settings, settings_field, True)
        
        return True

    @staticmethod
    def send_push_notification(
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        channel_id: str = 'default',
        priority: str = 'high',
        sound: str = 'default',
        badge: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send push notification to Expo push tokens
        
        Args:
            tokens: List of Expo push tokens
            title: Notification title
            body: Notification body/message
            data: Additional data for the notification
            channel_id: Android notification channel
            priority: Notification priority (default, normal, high)
            sound: Notification sound (default or custom sound file)
            badge: Badge count to display on app icon (iOS)
        
        Returns:
            Response from Expo push API
        """
        if not tokens:
            return {'success': False, 'message': 'No tokens provided'}
        
        messages = []
        for token in tokens:
            message = {
                'to': token,
                'title': title,
                'body': body,
                'sound': sound,
                'priority': priority,
                'channelId': channel_id,
            }
            
            if data:
                message['data'] = data
            
            if badge is not None:
                message['badge'] = badge
            
            messages.append(message)
        
        try:
            response = requests.post(
                EXPO_PUSH_URL,
                json=messages,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate',
                }
            )
            
            result = response.json()
            logger.info(f'Push notification sent: {result}')
            return {'success': True, 'data': result}
            
        except Exception as e:
            logger.error(f'Error sending push notification: {e}')
            return {'success': False, 'error': str(e)}

    @staticmethod
    def create_and_send_notification(
        user: User,
        notification_type: str,
        title: str,
        message: str,
        related_user: Optional[User] = None,
        related_activity_id: Optional[int] = None,
        related_friendship_id: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
        channel_id: str = 'default'
    ) -> Optional[Notification]:
        """
        Create a notification in the database and send push notification
        
        Args:
            user: Target user to receive notification
            notification_type: Type of notification (e.g., 'friend_request', 'activity_update')
            title: Notification title
            message: Notification message
            related_user: Related user (optional)
            related_activity_id: Related activity ID (optional)
            related_friendship_id: Related friendship ID (optional)
            data: Additional data (optional)
            channel_id: Android notification channel
        
        Returns:
            Created Notification object or None if failed
        """
        # Create notification in database
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_user=related_user,
            related_activity_id=related_activity_id,
            related_friendship_id=related_friendship_id,
            data=data or {}
        )
        
        # Check if user should receive push notification
        if not PushNotificationService.should_send_notification(user, notification_type):
            logger.info(f'Push notification skipped for user {user.id} - disabled in settings')
            return notification
        
        # Get user's push tokens
        tokens = PushNotificationService.get_user_push_tokens(user)
        
        if tokens:
            # Add notification ID to data
            push_data = data.copy() if data else {}
            push_data['notification_id'] = notification.id
            push_data['notification_type'] = notification_type
            
            # Send push notification
            result = PushNotificationService.send_push_notification(
                tokens=tokens,
                title=title,
                body=message,
                data=push_data,
                channel_id=channel_id
            )
            
            if result.get('success'):
                notification.is_pushed = True
                notification.pushed_at = timezone.now()
                notification.save(update_fields=['is_pushed', 'pushed_at'])
        else:
            logger.info(f'No push tokens found for user {user.id}')
        
        return notification

    @staticmethod
    def send_friend_request_notification(from_user: User, to_user: User, friendship_id: int):
        """Send notification when someone sends a friend request"""
        return PushNotificationService.create_and_send_notification(
            user=to_user,
            notification_type='friend_request',
            title='Yeni dostluq sorğusu',
            message=f'{from_user.get_full_name()} sizə dostluq sorğusu göndərdi',
            related_user=from_user,
            related_friendship_id=friendship_id,
            channel_id='friends',
            data={'screen': 'Friends', 'tab': 'pending'}
        )

    @staticmethod
    def send_friend_accepted_notification(from_user: User, to_user: User, friendship_id: int):
        """Send notification when friend request is accepted"""
        return PushNotificationService.create_and_send_notification(
            user=to_user,
            notification_type='friend_accepted',
            title='Dostluq sorğusu qəbul edildi',
            message=f'{from_user.get_full_name()} dostluq sorğunuzu qəbul etdi',
            related_user=from_user,
            related_friendship_id=friendship_id,
            channel_id='friends',
            data={'screen': 'UserProfile', 'userId': from_user.id}
        )

    @staticmethod
    def send_new_message_notification(from_user: User, to_user: User, message_preview: str):
        """Send notification for new message"""
        return PushNotificationService.create_and_send_notification(
            user=to_user,
            notification_type='new_message',
            title=from_user.get_full_name(),
            message=message_preview[:100] + ('...' if len(message_preview) > 100 else ''),
            related_user=from_user,
            channel_id='messages',
            data={'screen': 'Chat', 'userId': from_user.id}
        )

    @staticmethod
    def send_activity_reminder(user: User, activity_id: int, activity_title: str, starts_in: str):
        """Send activity reminder notification"""
        return PushNotificationService.create_and_send_notification(
            user=user,
            notification_type='activity_reminder',
            title='Aktivitə xatırlatması',
            message=f'"{activity_title}" aktivitəsi {starts_in} başlayır',
            related_activity_id=activity_id,
            channel_id='activity-reminders',
            data={'screen': 'ActivityDetail', 'activityId': activity_id}
        )

    @staticmethod
    def send_activity_join_request_notification(
        organizer: User, 
        requester: User, 
        activity_id: int,
        activity_title: str
    ):
        """Send notification when someone wants to join an activity"""
        return PushNotificationService.create_and_send_notification(
            user=organizer,
            notification_type='activity_join_request',
            title='Yeni qoşulma sorğusu',
            message=f'{requester.get_full_name()} "{activity_title}" aktivitənizə qoşulmaq istəyir',
            related_user=requester,
            related_activity_id=activity_id,
            channel_id='default',
            data={'screen': 'ActivityDetail', 'activityId': activity_id}
        )

    @staticmethod
    def send_activity_update_notification(
        user: User, 
        activity_id: int, 
        activity_title: str,
        update_type: str = 'updated'
    ):
        """Send notification when an activity is updated"""
        messages = {
            'updated': f'"{activity_title}" aktivitəsində dəyişiklik edildi',
            'cancelled': f'"{activity_title}" aktivitəsi ləğv edildi',
            'starting_soon': f'"{activity_title}" aktivitəsi tezliklə başlayır',
        }
        
        titles = {
            'updated': 'Aktivitə yeniləndi',
            'cancelled': 'Aktivitə ləğv edildi',
            'starting_soon': 'Aktivitə tezliklə başlayır',
        }
        
        notification_types = {
            'updated': 'activity_update',
            'cancelled': 'activity_cancelled',
            'starting_soon': 'activity_starting_soon',
        }
        
        return PushNotificationService.create_and_send_notification(
            user=user,
            notification_type=notification_types.get(update_type, 'activity_update'),
            title=titles.get(update_type, 'Aktivitə yeniləndi'),
            message=messages.get(update_type, f'"{activity_title}" aktivitəsində dəyişiklik'),
            related_activity_id=activity_id,
            channel_id='activity-reminders',
            data={'screen': 'ActivityDetail', 'activityId': activity_id}
        )


# Create a singleton instance
push_service = PushNotificationService()

