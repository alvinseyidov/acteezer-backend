from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
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
    """Step 1: Phone number and password registration"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if not phone:
            messages.error(request, 'Zəhmət olmasa telefon nömrəsini daxil edin.')
            return render(request, 'accounts/phone_registration.html')
        
        if not password or not password_confirm:
            messages.error(request, 'Zəhmət olmasa şifrəni daxil edin.')
            return render(request, 'accounts/phone_registration.html')
        
        if password != password_confirm:
            messages.error(request, 'Şifrələr uyğun gəlmir.')
            return render(request, 'accounts/phone_registration.html')
        
        if len(password) < 6:
            messages.error(request, 'Şifrə ən azı 6 simvoldan ibarət olmalıdır.')
            return render(request, 'accounts/phone_registration.html')
        
        # Check if user already exists
        if User.objects.filter(phone=phone).exists():
            messages.error(request, 'Bu telefon nömrəsi artıq qeydiyyatdan keçib.')
            return render(request, 'accounts/phone_registration.html')
        
        # Create new user
        user = User.objects.create(
            phone=phone,
            registration_step=1,
            is_phone_verified=True
        )
        user.set_password(password)
        user.save()
        
        # Login user
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Store phone in session for next step
        request.session['phone'] = phone
        
        # Redirect to next step (full name registration)
        return redirect('accounts:full_name_registration')
    
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
            
            # Check if OTP is valid (1234 for everyone for now, or the stored OTP)
            if (otp == '1234' or (user.otp_code == otp and 
                user.otp_created_at and 
                timezone.now() - user.otp_created_at < timedelta(minutes=5))):
                
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
        gender = request.POST.get('gender')
        
        if first_name and last_name and gender:
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.gender = gender
            request.user.registration_step = 2
            request.user.save()
            
            return redirect('accounts:languages_registration')
        else:
            messages.error(request, 'Zəhmət olmasa bütün məlumatları doldurun.')
    
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
            
            return redirect('accounts:birthday_registration')
        else:
            messages.error(request, 'Please select at least one language.')
    
    languages = Language.objects.all()
    user_languages = request.user.languages.all()
    
    # Auto-select Azerbaijan if no languages selected
    if not user_languages.exists():
        azerbaijan_lang = Language.objects.filter(code='az').first()
        if azerbaijan_lang:
            user_languages = [azerbaijan_lang]
    
    return render(request, 'accounts/languages_registration.html', {
        'languages': languages,
        'user_languages': user_languages,
        'default_country': 'Azerbaijan',
        'default_language': 'az'
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
        
        if bio and len(bio.strip()) >= 20:
            request.user.bio = bio.strip()
            request.user.registration_step = 6
            request.user.save()
            
            return redirect('accounts:interests_registration')
        else:
            messages.error(request, 'Zəhmət olmasa ən azı 20 simvol daxil edin.')
    
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
            
            return redirect('accounts:location_registration')
        else:
            messages.error(request, 'Please select at least one interest.')
    
    # Get all interests, categorized
    all_interests = Interest.objects.all()
    general_interests = Interest.objects.filter(is_general=True)
    user_interests = request.user.interests.all()
    
    # Create a mapping of category to related categories for showing related interests
    # When user selects an interest from a category, show interests from related categories
    category_relations = {
        'beauty': ['beauty', 'lifestyle'],  # Selecting beauty shows beauty + lifestyle
        'lifestyle': ['lifestyle', 'beauty', 'nature'],  # Selecting lifestyle shows lifestyle + beauty + nature
        'travel': ['travel', 'nature'],
        'music': ['music', 'arts'],
        'arts': ['arts', 'music'],
        'food': ['food', 'lifestyle'],
        'sports': ['sports', 'health', 'nature'],
        'health': ['health', 'sports', 'nature'],
        'nature': ['nature', 'health', 'lifestyle'],
        'education': ['education', 'arts'],
        'tech': ['tech', 'education'],
        'social': ['social', 'lifestyle'],
    }
    
    import json
    return render(request, 'accounts/interests_registration.html', {
        'interests': all_interests,
        'general_interests': general_interests,
        'user_interests': user_interests,
        'category_relations_json': json.dumps(category_relations),
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
        print("=" * 60)
        print("📋 POST request received")
        print(f"📋 User: {request.user.id} ({request.user.phone})")
        print(f"📋 Registration step before: {request.user.registration_step}")
        print("=" * 60)
        
        city = request.POST.get('city')
        address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        print(f"📊 POST data received:")
        print(f"   city='{city}'")
        print(f"   address='{address}'")
        print(f"   latitude='{latitude}'")
        print(f"   longitude='{longitude}'")
        print(f"📊 All POST keys: {list(request.POST.keys())}")
        
        if city and latitude and longitude:
            print("✅ All required fields present, updating user")
            try:
                request.user.city = city
                request.user.address = address or ''
                request.user.latitude = float(latitude)
                request.user.longitude = float(longitude)
                request.user.registration_step = 8
                request.user.is_registration_complete = True
                
                print(f"📝 User data before save:")
                print(f"   city: {request.user.city}")
                print(f"   latitude: {request.user.latitude}")
                print(f"   longitude: {request.user.longitude}")
                print(f"   registration_step: {request.user.registration_step}")
                print(f"   is_registration_complete: {request.user.is_registration_complete}")
                
                request.user.save(update_fields=['city', 'address', 'latitude', 'longitude', 'registration_step', 'is_registration_complete'])
                
                print(f"✅ User saved successfully!")
                print(f"🎉 Registration complete: {request.user.is_registration_complete}")
                
                redirect_url = reverse('accounts:registration_complete')
                print(f"🔄 Redirecting to: {redirect_url}")
                print("=" * 60)
                
                # Use HttpResponseRedirect for explicit redirect
                return HttpResponseRedirect(redirect_url)
            except Exception as e:
                import traceback
                print(f"❌ Error saving user: {e}")
                print(traceback.format_exc())
                print("=" * 60)
                messages.error(request, f'Error saving registration: {e}')
        else:
            print("❌ Missing required fields")
            missing_fields = []
            if not city: missing_fields.append('city')
            if not latitude: missing_fields.append('latitude')
            if not longitude: missing_fields.append('longitude')
            print(f"Missing fields: {missing_fields}")
            print("=" * 60)
            messages.error(request, 'Please select your city and pin location on the map.')
    else:
        print("📄 GET request - rendering form")
    
    return render(request, 'accounts/location_registration.html')


@login_required
def registration_complete(request):
    """Registration completion page"""
    if not request.user.is_registration_complete:
        return redirect('accounts:phone_registration')
    
    # Get user's interests for display
    user_interests = request.user.interests.all()
    
    return render(request, 'accounts/registration_complete.html', {
        'user_interests': user_interests
    })


@login_required
def profile(request):
    """User profile view"""
    from activities.models import ActivityParticipant, Activity
    from .models import UserImage
    
    # Get primary image
    primary_image = UserImage.objects.filter(user=request.user, is_primary=True).first()
    if not primary_image:
        primary_image = UserImage.objects.filter(user=request.user).first()
    
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
        'primary_image': primary_image,
        'organized_activities_count': organized_activities_count,
        'joined_activities_count': joined_activities_count,
        'completed_activities_count': completed_activities_count,
        'recent_activities': recent_activities,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile"""
    from .models import Language, Interest, UserImage
    from django.contrib import messages
    
    if request.method == 'POST':
        user = request.user
        
        # Check if this is just an image operation (primary image change or deletion)
        primary_image_id = request.POST.get('primary_image_id')
        delete_image_ids = request.POST.getlist('delete_images')
        new_images = request.FILES.getlist('new_images')
        
        is_image_only_operation = (primary_image_id or delete_image_ids) and not request.POST.get('first_name')
        
        # Handle primary image change
        if primary_image_id:
            try:
                # Set new primary image
                UserImage.objects.filter(user=user, id=primary_image_id).update(is_primary=True)
                UserImage.objects.filter(user=user).exclude(id=primary_image_id).update(is_primary=False)
                messages.success(request, 'Əsas şəkil dəyişdirildi!')
            except Exception:
                pass
        
        # Handle image deletion
        if delete_image_ids:
            images_to_delete = UserImage.objects.filter(user=user, id__in=delete_image_ids)
            images_to_delete.delete()
            # If we deleted the primary image, make the first remaining image primary
            if UserImage.objects.filter(user=user, is_primary=True).count() == 0:
                first_image = UserImage.objects.filter(user=user).first()
                if first_image:
                    first_image.is_primary = True
                    first_image.save()
            messages.success(request, 'Şəkil(lər) silindi!')
        
        # Handle image uploads
        if new_images:
            existing_count = user.images.count()
            for i, image in enumerate(new_images):
                UserImage.objects.create(
                    user=user,
                    image=image,
                    order=existing_count + i + 1,
                    is_primary=(existing_count == 0 and i == 0)  # Make first image primary if no images exist
                )
            # If this was the first image, make it primary
            if existing_count == 0 and new_images:
                first_img = UserImage.objects.filter(user=user).first()
                if first_img:
                    first_img.is_primary = True
                    first_img.save()
            messages.success(request, 'Şəkil(lər) yükləndi!')
        
        # If it's just an image operation, redirect immediately
        if is_image_only_operation:
            return redirect('accounts:edit_profile')
        
        # Update basic info
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.bio = request.POST.get('bio', '').strip()
        
        # Update birthday
        birthday_str = request.POST.get('birthday', '').strip()
        if birthday_str:
            try:
                from datetime import datetime
                user.birthday = datetime.strptime(birthday_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Doğum tarixi düzgün formatda deyil.')
        
        # Update gender
        gender = request.POST.get('gender', '').strip()
        if gender:
            user.gender = gender
        else:
            user.gender = None
        
        # Update location
        user.city = request.POST.get('city', '').strip() or None
        user.address = request.POST.get('address', '').strip() or None
        
        # Update languages
        language_ids = request.POST.getlist('languages')
        user.languages.set(Language.objects.filter(id__in=language_ids))
        
        # Update interests
        interest_ids = request.POST.getlist('interests')
        user.interests.set(Interest.objects.filter(id__in=interest_ids))
        
        user.save()
        messages.success(request, 'Profil uğurla yeniləndi!')
        return redirect('accounts:profile')
    
    # GET request - show edit form
    languages = Language.objects.all().order_by('name')
    interests = Interest.objects.all().order_by('name')
    user_images = UserImage.objects.filter(user=request.user).order_by('order', 'uploaded_at')
    
    context = {
        'languages': languages,
        'interests': interests,
        'user_images': user_images,
    }
    return render(request, 'accounts/edit_profile.html', context)

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
    """Login page with phone and password"""
    if request.user.is_authenticated:
        # If already logged in, redirect to home
        return redirect('home')
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        
        if phone and password:
            try:
                user = User.objects.get(phone=phone)
                
                # Check password
                if user.check_password(password):
                    # Login user
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    
                    # Always redirect to home page after successful login
                    return redirect('home')
                else:
                    messages.error(request, 'Telefon və ya şifrə yanlışdır.')
            except User.DoesNotExist:
                messages.error(request, 'Telefon və ya şifrə yanlışdır.')
        else:
            messages.error(request, 'Zəhmət olmasa bütün xanaları doldurun.')
    
    return render(request, 'accounts/login.html')


def user_logout(request):
    """Logout user"""
    logout(request)
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


def user_detail(request, user_id):
    """View other user's public profile"""
    from activities.models import ActivityParticipant, Activity
    from django.utils import timezone
    
    try:
        profile_user = User.objects.select_related().prefetch_related('images', 'interests', 'languages').get(
            id=user_id,
            is_registration_complete=True,
            is_active=True
        )
    except User.DoesNotExist:
        from django.http import Http404
        raise Http404("User not found")
    
    # Get friendship status if current user is authenticated
    friendship_status = None
    if request.user.is_authenticated:
        friendship_status = Friendship.get_friendship_status(request.user, profile_user)
    
    # Get user's organized activities
    organized_activities = Activity.objects.filter(organizer=profile_user, status='published').order_by('-start_date')
    organized_activities_count = organized_activities.count()
    
    # Get user's joined activities (as participant)
    joined_participations = ActivityParticipant.objects.filter(
        user=profile_user, 
        status='approved'
    ).select_related('activity').order_by('-join_requested_at')
    joined_activities_count = joined_participations.count()
    
    # Get completed activities
    completed_participations = joined_participations.filter(
        activity__end_date__lt=timezone.now()
    )
    completed_activities_count = completed_participations.count()
    
    # Get recent activities (upcoming organized + joined)
    upcoming_organized = organized_activities.filter(start_date__gte=timezone.now())[:5]
    recent_joined = joined_participations.filter(activity__start_date__gte=timezone.now())[:5]
    
    # Get user images
    user_images = profile_user.images.all()
    primary_image = user_images.filter(is_primary=True).first() or user_images.first()
    
    context = {
        'profile_user': profile_user,
        'primary_image': primary_image,
        'user_images': user_images,
        'friendship_status': friendship_status,
        'organized_activities_count': organized_activities_count,
        'joined_activities_count': joined_activities_count,
        'completed_activities_count': completed_activities_count,
        'upcoming_organized': upcoming_organized,
        'recent_joined': recent_joined,
    }
    
    return render(request, 'accounts/user_detail.html', context)


@login_required
def settings(request):
    """User settings page"""
    from django.contrib.auth import update_session_auth_hash
    
    if request.method == 'POST':
        user = request.user
        action = request.POST.get('action')
        
        if action == 'change_password':
            # Change password
            old_password = request.POST.get('old_password', '').strip()
            new_password = request.POST.get('new_password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()
            
            if not old_password or not new_password or not confirm_password:
                messages.error(request, 'Bütün sahələr doldurulmalıdır.')
            elif new_password != confirm_password:
                messages.error(request, 'Yeni şifrələr uyğun gəlmir.')
            elif len(new_password) < 8:
                messages.error(request, 'Şifrə ən azı 8 simvol olmalıdır.')
            elif not user.check_password(old_password):
                messages.error(request, 'Köhnə şifrə düzgün deyil.')
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)  # Keep user logged in
                messages.success(request, 'Şifrə uğurla dəyişdirildi!')
                return redirect('accounts:settings')
        
        elif action == 'update_email':
            # Update email
            email = request.POST.get('email', '').strip()
            if email:
                user.email = email
                user.save()
                messages.success(request, 'Email uğurla yeniləndi!')
            else:
                messages.error(request, 'Email daxil edin.')
            return redirect('accounts:settings')
        
        elif action == 'update_phone':
            # Update phone (requires verification)
            phone = request.POST.get('phone', '').strip()
            if phone:
                # Check if phone is already taken
                if User.objects.filter(phone=phone).exclude(id=user.id).exists():
                    messages.error(request, 'Bu telefon nömrəsi artıq istifadə olunur.')
                else:
                    user.phone = phone
                    user.is_phone_verified = False  # Require re-verification
                    user.save()
                    messages.success(request, 'Telefon nömrəsi yeniləndi. Zəhmət olmasa yenidən təsdiqləyin.')
            else:
                messages.error(request, 'Telefon nömrəsi daxil edin.')
            return redirect('accounts:settings')
    
    return render(request, 'accounts/settings.html')