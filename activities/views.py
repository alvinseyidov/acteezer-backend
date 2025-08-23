from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Activity, ActivityCategory, ActivityParticipant
import logging

# Setup logging for debugging
logger = logging.getLogger(__name__)


def activities_list(request):
    """View for displaying list of activities with search and filtering functionality"""
    activities = Activity.objects.filter(status='published').select_related('category', 'organizer')
    categories = ActivityCategory.objects.all().order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        activities = activities.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(location_name__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        activities = activities.filter(category__category_type=category_filter)
    
    # District filter
    district_filter = request.GET.get('district', '')
    if district_filter:
        activities = activities.filter(district=district_filter)
    
    # Date filter
    date_filter = request.GET.get('date', '')
    now = timezone.now()
    if date_filter == 'today':
        activities = activities.filter(start_date__date=now.date())
    elif date_filter == 'tomorrow':
        tomorrow = now.date().replace(day=now.day + 1)
        activities = activities.filter(start_date__date=tomorrow)
    elif date_filter == 'week':
        week_later = now.date().replace(day=now.day + 7)
        activities = activities.filter(start_date__date__lte=week_later)
    elif date_filter == 'upcoming':
        activities = activities.filter(start_date__gt=now)
    
    # Price filter
    price_filter = request.GET.get('price', '')
    if price_filter == 'free':
        activities = activities.filter(is_free=True)
    elif price_filter == 'paid':
        activities = activities.filter(is_free=False)
    
    # Difficulty filter
    difficulty_filter = request.GET.get('difficulty', '')
    if difficulty_filter:
        activities = activities.filter(difficulty_level=difficulty_filter)
    
    # Participants filter
    participants_filter = request.GET.get('participants', '')
    if participants_filter == 'small':
        activities = activities.filter(max_participants__gte=2, max_participants__lte=10)
    elif participants_filter == 'medium':
        activities = activities.filter(max_participants__gte=11, max_participants__lte=25)
    elif participants_filter == 'large':
        activities = activities.filter(max_participants__gte=26, max_participants__lte=50)
    elif participants_filter == 'xlarge':
        activities = activities.filter(max_participants__gt=50)
    
    # Sorting
    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'date':
        activities = activities.order_by('start_date')
    elif sort_by == 'price_low':
        activities = activities.order_by('price')
    elif sort_by == 'price_high':
        activities = activities.order_by('-price')
    elif sort_by == 'newest':
        activities = activities.order_by('-created_at')
    else:  # featured
        activities = activities.order_by('-is_featured', 'start_date')
    
    # Pagination
    paginator = Paginator(activities, 12)  # Show 12 activities per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get featured activities for hero section
    featured_activities = Activity.objects.filter(
        status='published', 
        is_featured=True,
        start_date__gt=now
    )[:8]
    
    # Filter choices
    district_choices = Activity.DISTRICT_CHOICES
    difficulty_choices = Activity.DIFFICULTY_CHOICES
    
    context = {
        'page_obj': page_obj,
        'activities': page_obj.object_list,
        'categories': categories,
        'featured_activities': featured_activities,
        'district_choices': district_choices,
        'difficulty_choices': difficulty_choices,
        'search_query': search_query,
        'category_filter': category_filter,
        'district_filter': district_filter,
        'date_filter': date_filter,
        'price_filter': price_filter,
        'difficulty_filter': difficulty_filter,
        'sort_by': sort_by,
        'total_count': paginator.count,
    }
    
    return render(request, 'core/activities.html', context)


def activity_detail(request, pk):
    """View for displaying detailed information about a specific activity"""
    activity = get_object_or_404(Activity, pk=pk, status='published')
    
    # Get participants
    approved_participants = activity.participants.filter(status='approved').select_related('user')
    pending_participants = activity.participants.filter(status='pending').select_related('user')
    
    # Get user's participation status if logged in
    user_participation = None
    can_join = False
    join_message = ""
    can_chat = False
    
    if request.user.is_authenticated:
        user_participation = activity.participants.filter(user=request.user).first()
        can_join, join_message = activity.can_user_join(request.user)
        
        # Check if user can access chat (approved participants or organizer)
        can_chat = (user_participation and user_participation.status == 'approved') or request.user == activity.organizer
    
    # Get reviews
    reviews = activity.reviews.filter().select_related('reviewer')[:10]
    
    # Get comments
    comments = activity.comments.filter(parent=None).select_related('user').prefetch_related('replies__user')[:20]
    
    # Get related activities
    related_activities = Activity.objects.filter(
        category=activity.category,
        status='published'
    ).exclude(pk=activity.pk)[:4]
    
    context = {
        'activity': activity,
        'approved_participants': approved_participants,
        'pending_participants': pending_participants,
        'user_participation': user_participation,
        'can_join': can_join,
        'join_message': join_message,
        'can_chat': can_chat,
        'reviews': reviews,
        'comments': comments,
        'related_activities': related_activities,
        'page_title': f"{activity.title} - Acteezer",
    }
    
    return render(request, 'core/activity_detail.html', context)


@login_required
@require_POST
def join_activity(request, pk):
    """Handle activity join requests"""
    activity = get_object_or_404(Activity, pk=pk, status='published')
    
    can_join, message = activity.can_user_join(request.user)
    
    if can_join:
        participant_message = request.POST.get('message', '')
        
        ActivityParticipant.objects.create(
            activity=activity,
            user=request.user,
            message=participant_message,
            status='pending'
        )
        
        messages.success(request, 'Qoşulma sorğunuz göndərildi! Təşkilatçı tərəfindən cavab gözləyin.')
    else:
        messages.error(request, message)
    
    return redirect('activities:activity_detail', pk=pk)


@login_required
@require_POST
def cancel_join_request(request, pk):
    """Cancel a join request"""
    activity = get_object_or_404(Activity, pk=pk)
    
    try:
        participation = ActivityParticipant.objects.get(activity=activity, user=request.user)
        if participation.status in ['pending', 'approved']:
            participation.delete()
            messages.success(request, 'Qoşulma sorğunuz ləğv edildi.')
        else:
            messages.error(request, 'Bu sorğunu ləğv edə bilməzsiniz.')
    except ActivityParticipant.DoesNotExist:
        messages.error(request, 'Qoşulma sorğunuz tapılmadı.')
    
    return redirect('activities:activity_detail', pk=pk)


@login_required
@require_POST
def manage_participant(request, pk, participant_id):
    """Manage participant requests (approve/reject) - only for organizers"""
    activity = get_object_or_404(Activity, pk=pk, organizer=request.user)
    participant = get_object_or_404(ActivityParticipant, pk=participant_id, activity=activity)
    
    action = request.POST.get('action')
    organizer_response = request.POST.get('response', '')
    
    if action == 'approve':
        if activity.is_full:
            messages.error(request, 'Aktivitə doludur, daha çox iştirakçı qəbul edilə bilməz.')
        else:
            participant.status = 'approved'
            participant.organizer_response = organizer_response
            participant.save()
            messages.success(request, f'{participant.user.get_full_name()} təsdiqləndi.')
    elif action == 'reject':
        participant.status = 'rejected'
        participant.organizer_response = organizer_response
        participant.save()
        messages.success(request, f'{participant.user.get_full_name()} rədd edildi.')
    
    return redirect('activities:activity_detail', pk=pk)


@login_required
def create_activity(request):
    """Create new activity"""
    logger.info(f"Create activity view called. Method: {request.method}")
    print(f"[DEBUG] Create activity view - Method: {request.method}, User: {request.user}")
    
    if request.method == 'POST':
        logger.info("Processing POST request for activity creation")
        print("[DEBUG] Processing POST request for activity creation")
        try:
            # Log all POST data for debugging
            logger.info(f"POST data keys: {list(request.POST.keys())}")
            logger.info(f"FILES data keys: {list(request.FILES.keys())}")
            
            # Get form data
            title = request.POST.get('title', '').strip()
            category_id = request.POST.get('category')
            short_description = request.POST.get('short_description', '').strip()
            description = request.POST.get('description', '').strip()
            start_date = request.POST.get('start_date')
            start_time = request.POST.get('start_time')
            end_date = request.POST.get('end_date')
            end_time = request.POST.get('end_time')
            address = request.POST.get('address', '').strip()
            max_participants = request.POST.get('max_participants')
            price = request.POST.get('price', 0)
            requirements = request.POST.get('requirements', '').strip()
            
            logger.info(f"Basic form data - title: {title}, category_id: {category_id}, start_date: {start_date}, start_time: {start_time}")
            
            # Get new requirement fields
            min_age = request.POST.get('min_age')
            max_age = request.POST.get('max_age')
            required_languages = request.POST.getlist('required_languages')
            allowed_genders = request.POST.getlist('allowed_genders')
            
            logger.info(f"Requirements - min_age: {min_age}, max_age: {max_age}, languages: {required_languages}, genders: {allowed_genders}")
            
            # Filter out empty values from lists
            required_languages = [lang for lang in required_languages if lang]
            allowed_genders = [gender for gender in allowed_genders if gender]
            
            # Validation
            if not all([title, category_id, short_description, description, start_date, start_time, address, max_participants]):
                missing_fields = []
                if not title: missing_fields.append('title')
                if not category_id: missing_fields.append('category')
                if not short_description: missing_fields.append('short_description')
                if not description: missing_fields.append('description')
                if not start_date: missing_fields.append('start_date')
                if not start_time: missing_fields.append('start_time')
                if not address: missing_fields.append('address')
                if not max_participants: missing_fields.append('max_participants')
                
                logger.error(f"Missing required fields: {missing_fields}")
                messages.error(request, f'Bütün məcburi sahələri doldurun. Missing: {", ".join(missing_fields)}')
                raise ValueError("Missing required fields")
            
            # Parse dates
            logger.info(f"Parsing dates: {start_date} {start_time}")
            start_datetime = timezone.make_aware(
                datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
            )
            
            if end_date and end_time:
                end_datetime = timezone.make_aware(
                    datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
                )
                logger.info(f"End datetime parsed: {end_datetime}")
            else:
                # Default end time to 3 hours after start
                end_datetime = start_datetime + timedelta(hours=3)
                logger.info(f"End datetime auto-set to: {end_datetime}")
            
            # Validate dates
            if start_datetime <= timezone.now():
                logger.error(f"Start datetime {start_datetime} is in the past. Current time: {timezone.now()}")
                messages.error(request, 'Aktivitə tarixi indiki vaxtdan sonra olmalıdır.')
                raise ValueError("Invalid start date")
            
            if end_datetime <= start_datetime:
                logger.error(f"End datetime {end_datetime} is before start datetime {start_datetime}")
                messages.error(request, 'Bitmə tarixi başlama tarixindən sonra olmalıdır.')
                raise ValueError("Invalid end date")
            
            # Calculate duration in hours
            duration_delta = end_datetime - start_datetime
            duration_hours = max(1, int(duration_delta.total_seconds() / 3600))  # At least 1 hour
            logger.info(f"Calculated duration: {duration_hours} hours")
            
            # Get category
            logger.info(f"Getting category with id: {category_id}")
            category = get_object_or_404(ActivityCategory, id=category_id)
            
            # Create activity
            logger.info("Creating activity object")
            activity = Activity.objects.create(
                title=title,
                category=category,
                short_description=short_description,
                description=description,
                organizer=request.user,
                start_date=start_datetime,
                end_date=end_datetime,
                duration_hours=duration_hours,
                location_name=address,  # Use address as location_name for now
                address=address,
                max_participants=int(max_participants),
                price=float(price) if price else 0,
                requirements=requirements,
                min_age=int(min_age) if min_age else None,
                max_age=int(max_age) if max_age else None,
                allowed_genders=allowed_genders,
                status='published'
            )
            logger.info(f"Activity created with ID: {activity.pk}")
            
            # Add required languages
            if required_languages:
                logger.info(f"Setting required languages: {required_languages}")
                activity.required_languages.set(required_languages)
            
            # Handle image upload if provided
            if 'main_image' in request.FILES:
                logger.info("Processing main image upload")
                activity.main_image = request.FILES['main_image']
                activity.save()
            
            messages.success(request, f'Aktivitə "{title}" uğurla yaradıldı!')
            logger.info(f"Activity creation successful, redirecting to detail page")
            return redirect('activities:activity_detail', pk=activity.pk)
            
        except ValueError as e:
            logger.error(f"ValueError in activity creation: {e}")
            # Error messages already set above
            pass
        except Exception as e:
            logger.error(f"Unexpected error in activity creation: {e}", exc_info=True)
            messages.error(request, 'Aktivitə yaradılarkən xəta baş verdi. Zəhmət olmasa bütün sahələri düzgün doldurun və yenidən cəhd edin.')
    
    # GET request or error - show form
    logger.info("Showing activity creation form")
    from accounts.models import Language
    categories = ActivityCategory.objects.all().order_by('name')
    languages = Language.objects.all().order_by('name')
    
    logger.info(f"Form context: {len(categories)} categories, {len(languages)} languages")
    
    context = {
        'categories': categories,
        'languages': languages,
        'page_title': 'Yeni Aktivitə Yarat'
    }
    
    return render(request, 'activities/create_activity.html', context)