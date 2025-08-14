from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import random
import json

from .models import User, Language, Interest, UserImage, OTPVerification


def home(request):
    """Home page view"""
    return render(request, 'core/home.html')


def activities(request):
    """Activities page view"""
    return render(request, 'core/activities.html')


def about(request):
    """About us page view"""
    return render(request, 'core/about.html')


def contact(request):
    """Contact page view"""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Here you would typically save to database or send email
        # For now, just show success message
        messages.success(request, 'Mesajınız uğurla göndərildi! Tezliklə sizinlə əlaqə saxlayacağıq.')
        return redirect('contact')
    
    return render(request, 'core/contact.html')


def blog(request):
    """Blog list page view"""
    from .models import BlogPost, BlogCategory
    
    # Get published posts
    posts = BlogPost.objects.filter(is_published=True).select_related('author', 'category')
    
    # Get featured post
    featured_post = posts.filter(is_featured=True).first()
    
    # Get categories
    categories = BlogCategory.objects.all()
    
    # Exclude featured post from regular posts
    if featured_post:
        posts = posts.exclude(id=featured_post.id)
    
    context = {
        'posts': posts[:12],  # Limit to 12 posts
        'featured_post': featured_post,
        'categories': categories,
    }
    return render(request, 'core/blog.html', context)


def blog_detail(request, slug):
    """Blog detail page view"""
    from .models import BlogPost
    from django.shortcuts import get_object_or_404
    
    # Get the post
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Increment view count
    post.increment_views()
    
    # Get related posts from same category
    related_posts = BlogPost.objects.filter(
        category=post.category,
        is_published=True
    ).exclude(id=post.id)[:4]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'core/blog_detail.html', context)


def phone_registration(request):
    """Step 1: Phone number registration"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        
        if not phone:
            messages.error(request, 'Please enter a phone number.')
            return render(request, 'accounts/phone_registration.html')
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        
        # Create or get user
        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={'registration_step': 0}
        )
        
        # Save OTP
        user.otp_code = otp
        user.otp_created_at = timezone.now()
        user.save()
        
        # Create OTP verification record
        OTPVerification.objects.create(
            phone=phone,
            otp_code=otp
        )
        
        # In a real app, send SMS here
        # For development, we'll just show the OTP
        messages.info(request, f'OTP sent! For testing: {otp}')
        
        # Store phone in session for next step
        request.session['phone'] = phone
        return redirect('accounts:otp_verification')
    
    return render(request, 'accounts/phone_registration.html')


def otp_verification(request):
    """Step 2: OTP verification"""
    phone = request.session.get('phone')
    if not phone:
        return redirect('accounts:phone_registration')
    
    if request.method == 'POST':
        otp = request.POST.get('otp')
        
        try:
            user = User.objects.get(phone=phone)
            
            # Check if OTP is valid and not expired (5 minutes)
            if (user.otp_code == otp and 
                user.otp_created_at and 
                timezone.now() - user.otp_created_at < timedelta(minutes=5)):
                
                user.is_phone_verified = True
                user.registration_step = 1
                user.otp_code = None
                user.save()
                
                # Update OTP verification record
                otp_verification = OTPVerification.objects.filter(
                    phone=phone, otp_code=otp
                ).first()
                if otp_verification:
                    otp_verification.is_verified = True
                    otp_verification.save()
                
                # Login user
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, 'Phone verified successfully!')
                return redirect('accounts:full_name_registration')
            else:
                messages.error(request, 'Invalid or expired OTP.')
        
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('accounts:phone_registration')
    
    return render(request, 'accounts/otp_verification.html', {'phone': phone})


@login_required
def full_name_registration(request):
    """Step 3: First and Last name"""
    if request.user.registration_step < 1:
        return redirect('accounts:phone_registration')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if first_name and last_name:
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.registration_step = 2
            request.user.save()
            
            messages.success(request, 'Name saved successfully!')
            return redirect('accounts:languages_registration')
        else:
            messages.error(request, 'Please enter both first and last name.')
    
    return render(request, 'accounts/full_name_registration.html')


@login_required
def languages_registration(request):
    """Step 4: Language selection"""
    if request.user.registration_step < 2:
        return redirect('full_name_registration')
    
    if request.method == 'POST':
        language_ids = request.POST.getlist('languages')
        
        if language_ids:
            languages = Language.objects.filter(id__in=language_ids)
            request.user.languages.set(languages)
            request.user.registration_step = 3
            request.user.save()
            
            messages.success(request, 'Languages saved successfully!')
            return redirect('accounts:birthday_registration')
        else:
            messages.error(request, 'Please select at least one language.')
    
    languages = Language.objects.all()
    user_languages = request.user.languages.all()
    return render(request, 'accounts/languages_registration.html', {
        'languages': languages,
        'user_languages': user_languages
    })


@login_required
def birthday_registration(request):
    """Step 5: Birthday"""
    if request.user.registration_step < 3:
        return redirect('accounts:languages_registration')
    
    if request.method == 'POST':
        birthday = request.POST.get('birthday')
        
        if birthday:
            request.user.birthday = birthday
            request.user.registration_step = 4
            request.user.save()
            
            messages.success(request, 'Birthday saved successfully!')
            return redirect('accounts:images_registration')
        else:
            messages.error(request, 'Please enter your birthday.')
    
    return render(request, 'accounts/birthday_registration.html')


@login_required
def images_registration(request):
    """Step 6: Image upload (minimum 2)"""
    if request.user.registration_step < 4:
        return redirect('accounts:birthday_registration')
    
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        
        if len(images) >= 2:
            # Delete existing images
            request.user.images.all().delete()
            
            # Save new images
            for i, image in enumerate(images):
                UserImage.objects.create(
                    user=request.user,
                    image=image,
                    order=i + 1,
                    is_primary=(i == 0)
                )
            
            request.user.registration_step = 5
            request.user.save()
            
            messages.success(request, 'Images uploaded successfully!')
            return redirect('accounts:bio_registration')
        else:
            messages.error(request, 'Please upload at least 2 images.')
    
    user_images = request.user.images.all()
    return render(request, 'accounts/images_registration.html', {
        'user_images': user_images
    })


@login_required
def bio_registration(request):
    """Step 7: Bio"""
    if request.user.registration_step < 5:
        return redirect('accounts:images_registration')
    
    if request.method == 'POST':
        bio = request.POST.get('bio')
        
        if bio:
            request.user.bio = bio
            request.user.registration_step = 6
            request.user.save()
            
            messages.success(request, 'Bio saved successfully!')
            return redirect('accounts:interests_registration')
        else:
            messages.error(request, 'Please enter your bio.')
    
    return render(request, 'accounts/bio_registration.html')


@login_required
def interests_registration(request):
    """Step 8: Interests selection"""
    if request.user.registration_step < 6:
        return redirect('accounts:bio_registration')
    
    if request.method == 'POST':
        interest_ids = request.POST.getlist('interests')
        
        if interest_ids:
            interests = Interest.objects.filter(id__in=interest_ids)
            request.user.interests.set(interests)
            request.user.registration_step = 7
            request.user.save()
            
            messages.success(request, 'Interests saved successfully!')
            return redirect('accounts:location_registration')
        else:
            messages.error(request, 'Please select at least one interest.')
    
    interests = Interest.objects.all()
    user_interests = request.user.interests.all()
    return render(request, 'accounts/interests_registration.html', {
        'interests': interests,
        'user_interests': user_interests
    })


@login_required
def location_registration(request):
    """Step 9: Location and map pin"""
    if request.user.registration_step < 7:
        return redirect('accounts:interests_registration')
    
    if request.method == 'POST':
        city = request.POST.get('city')
        address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        if city and latitude and longitude:
            request.user.city = city
            request.user.address = address
            request.user.latitude = latitude
            request.user.longitude = longitude
            request.user.registration_step = 8
            request.user.is_registration_complete = True
            request.user.save()
            
            messages.success(request, 'Registration completed successfully!')
            return redirect('accounts:registration_complete')
        else:
            messages.error(request, 'Please select your city and pin location on the map.')
    
    return render(request, 'accounts/location_registration.html')


@login_required
def registration_complete(request):
    """Registration completion page"""
    if not request.user.is_registration_complete:
        return redirect('accounts:phone_registration')
    
    return render(request, 'accounts/registration_complete.html')


@login_required
def profile(request):
    """User profile view"""
    from activities.models import ActivityParticipant, Activity
    
    # Get user's organized activities
    organized_activities = Activity.objects.filter(organizer=request.user).order_by('-created_at')
    organized_activities_count = organized_activities.count()
    
    # Get user's joined activities (as participant)
    joined_participations = ActivityParticipant.objects.filter(
        user=request.user, 
        status='approved'
    ).select_related('activity').order_by('-join_requested_at')
    joined_activities_count = joined_participations.count()
    
    # Get completed activities (past activities user participated in)
    from django.utils import timezone
    completed_participations = joined_participations.filter(
        activity__end_date__lt=timezone.now()
    )
    completed_activities_count = completed_participations.count()
    
    # Get recent activities for timeline (last 10)
    recent_activities = list(joined_participations[:5]) + list(organized_activities[:5])
    recent_activities = sorted(recent_activities, key=lambda x: x.join_requested_at if hasattr(x, 'join_requested_at') else x.created_at, reverse=True)[:10]
    
    context = {
        'organized_activities_count': organized_activities_count,
        'joined_activities_count': joined_activities_count,
        'completed_activities_count': completed_activities_count,
        'recent_activities': recent_activities,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def my_activities(request):
    """User's organized activities"""
    from activities.models import Activity
    
    activities = Activity.objects.filter(organizer=request.user).order_by('-created_at')
    
    context = {
        'activities': activities,
        'page_title': 'Təşkil Etdiyim Aktivitələr'
    }
    return render(request, 'accounts/my_activities.html', context)

@login_required
def joined_activities(request):
    """User's joined activities"""
    from activities.models import ActivityParticipant
    
    participations = ActivityParticipant.objects.filter(
        user=request.user, 
        status='approved'
    ).select_related('activity').order_by('-join_requested_at')
    
    context = {
        'participations': participations,
        'page_title': 'Qoşulduğum Aktivitələr'
    }
    return render(request, 'accounts/joined_activities.html', context)

def user_login(request):
    """Login page"""
    if request.user.is_authenticated:
        if request.user.is_registration_complete:
            return redirect('accounts:registration_complete')
        else:
            # Redirect to appropriate registration step
            step_urls = [
                'accounts:phone_registration', 'accounts:otp_verification', 'accounts:full_name_registration',
                'accounts:languages_registration', 'accounts:birthday_registration', 'accounts:images_registration',
                'accounts:bio_registration', 'accounts:interests_registration', 'accounts:location_registration'
            ]
            if request.user.registration_step < len(step_urls):
                return redirect(step_urls[request.user.registration_step])
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        if phone and password:
            user = authenticate(request, username=phone, password=password)
            if user:
                login(request, user)
                if user.is_registration_complete:
                    return redirect('accounts:registration_complete')
                else:
                    # Redirect to appropriate registration step
                    step_urls = [
                        'phone_registration', 'otp_verification', 'full_name_registration',
                        'languages_registration', 'birthday_registration', 'images_registration',
                        'bio_registration', 'interests_registration', 'location_registration'
                    ]
                    if user.registration_step < len(step_urls):
                        return redirect(step_urls[user.registration_step])
            else:
                messages.error(request, 'Invalid phone number or password.')
        else:
            messages.error(request, 'Please enter both phone and password.')
    
    return render(request, 'accounts/login.html')


def user_logout(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

@login_required
def joined_activities(request):
    """User's joined activities"""
    from activities.models import ActivityParticipant
    
    participations = ActivityParticipant.objects.filter(
        user=request.user, 
        status='approved'
    ).select_related('activity').order_by('-join_requested_at')
    
    context = {
        'participations': participations,
        'page_title': 'Qoşulduğum Aktivitələr'
    }
    return render(request, 'accounts/joined_activities.html', context)

def user_login(request):
    """Login page"""
    if request.user.is_authenticated:
        if request.user.is_registration_complete:
            return redirect('accounts:registration_complete')
        else:
            # Redirect to appropriate registration step
            step_urls = [
                'accounts:phone_registration', 'accounts:otp_verification', 'accounts:full_name_registration',
                'accounts:languages_registration', 'accounts:birthday_registration', 'accounts:images_registration',
                'accounts:bio_registration', 'accounts:interests_registration', 'accounts:location_registration'
            ]
            if request.user.registration_step < len(step_urls):
                return redirect(step_urls[request.user.registration_step])
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        if phone and password:
            user = authenticate(request, username=phone, password=password)
            if user:
                login(request, user)
                if user.is_registration_complete:
                    return redirect('accounts:registration_complete')
                else:
                    # Redirect to appropriate registration step
                    step_urls = [
                        'phone_registration', 'otp_verification', 'full_name_registration',
                        'languages_registration', 'birthday_registration', 'images_registration',
                        'bio_registration', 'interests_registration', 'location_registration'
                    ]
                    if user.registration_step < len(step_urls):
                        return redirect(step_urls[user.registration_step])
            else:
                messages.error(request, 'Invalid phone number or password.')
        else:
            messages.error(request, 'Please enter both phone and password.')
    
    return render(request, 'accounts/login.html')


def user_logout(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')
