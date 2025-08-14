from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Activity, ActivityParticipant, ActivityMessage


@login_required
@require_POST
def send_message(request, activity_id):
    """Send a chat message in activity group chat"""
    activity = get_object_or_404(Activity, id=activity_id)
    
    # Check if user is an approved participant or organizer
    user_participation = ActivityParticipant.objects.filter(
        activity=activity, 
        user=request.user, 
        status='approved'
    ).first()
    
    if not user_participation and request.user != activity.organizer:
        return JsonResponse({'error': 'Yalnız qoşulmuş iştirakçılar mesaj yaza bilər'}, status=403)
    
    message_text = request.POST.get('message', '').strip()
    if not message_text:
        return JsonResponse({'error': 'Mesaj boş ola bilməz'}, status=400)
    
    if len(message_text) > 1000:
        return JsonResponse({'error': 'Mesaj çox uzundur'}, status=400)
    
    message = ActivityMessage.objects.create(
        activity=activity,
        user=request.user,
        message=message_text
    )
    
    return JsonResponse({
        'success': True,
        'message': {
            'id': message.id,
            'user_name': request.user.get_full_name(),
            'message': message.message,
            'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
            'can_edit': True,
            'can_delete': True
        }
    })


@login_required
def get_messages(request, activity_id):
    """Get chat messages for activity"""
    activity = get_object_or_404(Activity, id=activity_id)
    
    # Check if user is an approved participant or organizer
    user_participation = ActivityParticipant.objects.filter(
        activity=activity, 
        user=request.user, 
        status='approved'
    ).first()
    
    if not user_participation and request.user != activity.organizer:
        return JsonResponse({'error': 'Bu söhbətə girişiniz yoxdur'}, status=403)
    
    # Get last 50 messages
    messages = ActivityMessage.objects.filter(activity=activity).select_related('user').order_by('-created_at')[:50]
    messages = list(reversed(messages))  # Show oldest first
    
    messages_data = []
    for message in messages:
        messages_data.append({
            'id': message.id,
            'user_name': message.user.get_full_name(),
            'user_id': message.user.id,
            'message': message.message,
            'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
            'is_edited': message.is_edited,
            'can_edit': message.can_edit(request.user),
            'can_delete': message.can_delete(request.user)
        })
    
    return JsonResponse({'messages': messages_data})


@login_required
@require_POST
def edit_message(request, activity_id, message_id):
    """Edit a chat message"""
    activity = get_object_or_404(Activity, id=activity_id)
    message = get_object_or_404(ActivityMessage, id=message_id, activity=activity)
    
    if not message.can_edit(request.user):
        return JsonResponse({'error': 'Bu mesajı redaktə etmək icazəniz yoxdur'}, status=403)
    
    new_message_text = request.POST.get('message', '').strip()
    if not new_message_text:
        return JsonResponse({'error': 'Mesaj boş ola bilməz'}, status=400)
    
    if len(new_message_text) > 1000:
        return JsonResponse({'error': 'Mesaj çox uzundur'}, status=400)
    
    message.message = new_message_text
    message.is_edited = True
    message.save()
    
    return JsonResponse({
        'success': True,
        'message': {
            'id': message.id,
            'message': message.message,
            'is_edited': True
        }
    })


@login_required
@require_POST
def delete_message(request, activity_id, message_id):
    """Delete a chat message"""
    activity = get_object_or_404(Activity, id=activity_id)
    message = get_object_or_404(ActivityMessage, id=message_id, activity=activity)
    
    if not message.can_delete(request.user):
        return JsonResponse({'error': 'Bu mesajı silmək icazəniz yoxdur'}, status=403)
    
    message.delete()
    
    return JsonResponse({'success': True})
