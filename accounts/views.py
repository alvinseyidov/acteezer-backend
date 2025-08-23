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

from .models import User, Language, Interest, UserImage, OTPVerification, Newsletter, Friendship


def home(request):
    """Home page view"""
    from activities.models import Activity, ActivityCategory
    
    # Get latest published activities (limit to 6 for home page)
    latest_activities = Activity.objects.filter(
        status='published',
        start_date__gte=timezone.now().date()
    ).select_related('category', 'organizer').order_by('start_date')[:6]
    
    # Get popular categories
    popular_categories = ActivityCategory.objects.all()[:8]
    
    context = {
        'latest_activities': latest_activities,
        'popular_categories': popular_categories,
    }
    
    return render(request, 'core/home.html', context)


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
            otp_code=otp,
            purpose='registration'
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
                    phone=phone, otp_code=otp, purpose='registration'
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
    print(f"🔍 location_registration called for user: {request.user.id} ({request.user.phone})")
    print(f"📊 User registration step: {request.user.registration_step}")
    
    if request.user.registration_step < 7:
        print(f"❌ User registration step {request.user.registration_step} < 7, redirecting to interests")
        return redirect('accounts:interests_registration')
    
    if request.method == 'POST':
        print("📋 POST request received")
        city = request.POST.get('city')
        address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        print(f"📊 POST data received: city='{city}', address='{address}', latitude='{latitude}', longitude='{longitude}'")
        
        if city and latitude and longitude:
            print("✅ All required fields present, updating user")
            try:
                request.user.city = city
                request.user.address = address
                request.user.latitude = latitude
                request.user.longitude = longitude
                request.user.registration_step = 8
                request.user.is_registration_complete = True
                request.user.save()
                
                print(f"✅ User updated successfully: {request.user.city}, {request.user.latitude}, {request.user.longitude}")
                print(f"🎉 Registration complete: {request.user.is_registration_complete}")
                
                messages.success(request, 'Registration completed successfully!')
                print("🔄 Redirecting to registration_complete")
                return redirect('accounts:registration_complete')
            except Exception as e:
                print(f"❌ Error saving user: {e}")
                messages.error(request, f'Error saving registration: {e}')
        else:
            print("❌ Missing required fields")
            missing_fields = []
            if not city: missing_fields.append('city')
            if not latitude: missing_fields.append('latitude')
            if not longitude: missing_fields.append('longitude')
            print(f"Missing fields: {missing_fields}")
            messages.error(request, 'Please select your city and pin location on the map.')
    else:
        print("📄 GET request - rendering form")
    
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
    """Login page - Step 1: Phone number entry"""
    if request.user.is_authenticated:
        if request.user.is_registration_complete:
            return redirect('home')
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
        
        if phone:
            try:
                # Check if user exists with this phone number
                user = User.objects.get(phone=phone)
                
                # Generate OTP for login
                otp = str(random.randint(100000, 999999))
                
                # Save OTP
                user.otp_code = otp
                user.otp_created_at = timezone.now()
                user.save()
                
                # Create OTP verification record for login
                OTPVerification.objects.create(
                    phone=phone,
                    otp_code=otp,
                    purpose='login'
                )
                
                # In a real app, send SMS here
                # For development, we'll just show the OTP
                messages.info(request, f'OTP sent to your phone! For testing: {otp}')
                
                # Store phone in session for OTP verification
                request.session['login_phone'] = phone
                return redirect('accounts:login_otp_verification')
                
            except User.DoesNotExist:
                messages.error(request, 'Bu telefon nömrəsi ilə qeydiyyat tapılmadı. Zəhmət olmasa qeydiyyatdan keçin.')
        else:
            messages.error(request, 'Zəhmət olmasa telefon nömrənizi daxil edin.')
    
    return render(request, 'accounts/login.html')


def login_otp_verification(request):
    """Login OTP verification - Step 2: OTP verification"""
    phone = request.session.get('login_phone')
    if not phone:
        messages.error(request, 'OTP sorğusu vaxtı keçib. Yenidən cəhd edin.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        print(f"[DEBUG] POST request received. POST data: {request.POST}")
        print(f"[DEBUG] CSRF token: {request.POST.get('csrfmiddlewaretoken', 'NOT FOUND')}")
        otp = request.POST.get('otp')
        print(f"[DEBUG] OTP received: {otp}")
        
        if otp:
            try:
                user = User.objects.get(phone=phone)
                
                # Check if OTP is valid and not expired (5 minutes)
                if (user.otp_code == otp and 
                    user.otp_created_at and 
                    timezone.now() - user.otp_created_at < timedelta(minutes=5)):
                    
                    # Clear OTP
                    user.otp_code = None
                    user.otp_created_at = None
                    user.save()
                    
                    # Update OTP verification record
                    otp_verification = OTPVerification.objects.filter(
                        phone=phone, otp_code=otp, purpose='login'
                    ).first()
                    if otp_verification:
                        otp_verification.is_verified = True
                        otp_verification.save()
                    
                    # Login user
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    
                    # Clear session data
                    if 'login_phone' in request.session:
                        del request.session['login_phone']
                    
                    messages.success(request, 'Uğurla daxil oldunuz!')
                    
                    # Redirect based on registration status
                    if user.is_registration_complete:
                        return redirect('home')
                    else:
                        # Redirect to appropriate registration step
                        step_urls = [
                            'accounts:phone_registration', 'accounts:otp_verification', 'accounts:full_name_registration',
                            'accounts:languages_registration', 'accounts:birthday_registration', 'accounts:images_registration',
                            'accounts:bio_registration', 'accounts:interests_registration', 'accounts:location_registration'
                        ]
                        if user.registration_step < len(step_urls):
                            return redirect(step_urls[user.registration_step])
                        return redirect('accounts:registration_complete')
                else:
                    messages.error(request, 'Yanlış və ya vaxtı keçmiş OTP kodu.')
            
            except User.DoesNotExist:
                messages.error(request, 'İstifadəçi tapılmadı.')
                return redirect('accounts:login')
        else:
            messages.error(request, 'Zəhmət olmasa OTP kodunu daxil edin.')
    
    return render(request, 'accounts/login_otp.html', {'phone': phone})


def user_logout(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')


@csrf_exempt
def newsletter_subscribe(request):
    """Handle newsletter subscription"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'message': 'Email ünvanı tələb olunur.'
                })
            
            # Check if email is already subscribed
            if Newsletter.objects.filter(email=email).exists():
                return JsonResponse({
                    'success': False,
                    'message': 'Bu email ünvanı artıq abunəlik siyahısındadır.'
                })
            
            # Check if user is logged in and link the subscription
            user = request.user if request.user.is_authenticated else None
            
            # Create newsletter subscription
            newsletter = Newsletter.objects.create(
                email=email,
                user=user
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Təbriklər! Xəbər bülleteni üçün uğurla abunə oldunuz.'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Yanlış məlumat formatı.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Bir xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Yanlış sorğu metodu.'
    })


def people_list(request):
    """People listing page with search functionality"""
    query = request.GET.get('q', '').strip()
    city_filter = request.GET.get('city', '')
    interest_filter = request.GET.get('interest', '')
    age_min = request.GET.get('age_min', '')
    age_max = request.GET.get('age_max', '')
    
    # Base queryset - exclude current user and get completed registrations only
    users = User.objects.filter(
        is_registration_complete=True,
        is_active=True
    ).exclude(id=request.user.id if request.user.is_authenticated else None).select_related().prefetch_related('languages', 'interests', 'images')
    
    # Search by name or bio
    if query:
        from django.db.models import Q
        users = users.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(bio__icontains=query)
        )
    
    # Filter by city
    if city_filter:
        users = users.filter(city__icontains=city_filter)
    
    # Filter by interest
    if interest_filter:
        users = users.filter(interests__id=interest_filter)
    
    # Filter by age range
    if age_min or age_max:
        from datetime import date
        today = date.today()
        
        if age_min:
            try:
                min_birth_year = today.year - int(age_min)
                users = users.filter(birthday__year__lte=min_birth_year)
            except ValueError:
                pass
        
        if age_max:
            try:
                max_birth_year = today.year - int(age_max)
                users = users.filter(birthday__year__gte=max_birth_year)
            except ValueError:
                pass
    
    # Get friendship statuses for current user
    if request.user.is_authenticated:
        # Add friendship status to each user object
        for user_obj in users:
            user_obj.friendship_status = Friendship.get_friendship_status(request.user, user_obj)
    
    # Order by latest joined
    users = users.order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(users, 12)  # 12 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all cities and interests for filters
    cities = User.objects.filter(
        is_registration_complete=True,
        city__isnull=False
    ).exclude(city='').values_list('city', flat=True).distinct().order_by('city')
    
    interests = Interest.objects.all().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'cities': cities,
        'interests': interests,
        'query': query,
        'city_filter': city_filter,
        'interest_filter': interest_filter,
        'age_min': age_min,
        'age_max': age_max,
    }
    
    return render(request, 'accounts/people_list.html', context)


@login_required
def send_friend_request(request):
    """Send a friend request via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            
            if not user_id:
                return JsonResponse({
                    'success': False,
                    'message': 'İstifadəçi ID-si tələb olunur.'
                })
            
            try:
                to_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'İstifadəçi tapılmadı.'
                })
            
            # Check if users are already friends or have pending request
            existing_status = Friendship.get_friendship_status(request.user, to_user)
            if existing_status:
                return JsonResponse({
                    'success': False,
                    'message': 'Artıq dostluq sorğusu mövcuddur.'
                })
            
            # Create friend request
            friendship = Friendship.objects.create(
                from_user=request.user,
                to_user=to_user,
                status='pending'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Dostluq sorğusu göndərildi!'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Yanlış məlumat formatı.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Bir xəta baş verdi.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Yanlış sorğu metodu.'
    })


@login_required
def respond_friend_request(request):
    """Accept or reject a friend request via AJAX"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            friendship_id = data.get('friendship_id')
            action = data.get('action')  # 'accept' or 'reject'
            
            if not friendship_id or action not in ['accept', 'reject']:
                return JsonResponse({
                    'success': False,
                    'message': 'Yanlış parametrlər.'
                })
            
            try:
                friendship = Friendship.objects.get(
                    id=friendship_id,
                    to_user=request.user,
                    status='pending'
                )
            except Friendship.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Dostluq sorğusu tapılmadı.'
                })
            
            if action == 'accept':
                friendship.status = 'accepted'
                message = 'Dostluq sorğusu qəbul edildi!'
            else:
                friendship.status = 'rejected'
                message = 'Dostluq sorğusu rədd edildi.'
            
            friendship.save()
            
            return JsonResponse({
                'success': True,
                'message': message
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Yanlış məlumat formatı.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Bir xəta baş verdi.'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Yanlış sorğu metodu.'
    })


@login_required
def friend_requests(request):
    """View pending friend requests"""
    # Received friend requests
    received_requests = Friendship.objects.filter(
        to_user=request.user,
        status='pending'
    ).select_related('from_user').prefetch_related('from_user__images', 'from_user__interests')
    
    # Sent friend requests
    sent_requests = Friendship.objects.filter(
        from_user=request.user,
        status='pending'
    ).select_related('to_user').prefetch_related('to_user__images', 'to_user__interests')
    
    context = {
        'received_requests': received_requests,
        'sent_requests': sent_requests,
    }
    
    return render(request, 'accounts/friend_requests.html', context)


@login_required
def friends_list(request):
    """View user's friends list"""
    friends = Friendship.get_friends(request.user).prefetch_related('images', 'interests')
    
    context = {
        'friends': friends,
    }
    
    return render(request, 'accounts/friends_list.html', context)