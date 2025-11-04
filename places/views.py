from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Case, When
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Place, PlaceCategory, PlaceFavorite


def places_list(request):
    """Enhanced view for displaying list of places with advanced TripAdvisor-style features"""
    places = Place.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'reviews')
    categories = PlaceCategory.objects.all().order_by('name')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        places = places.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        places = places.filter(category__category_type=category_filter)
    
    # District filter
    district_filter = request.GET.get('district', '')
    if district_filter:
        places = places.filter(district=district_filter)
    
    # Price range filter
    price_filter = request.GET.get('price', '')
    if price_filter:
        places = places.filter(price_range=price_filter)
    
    # Rating filter
    min_rating = request.GET.get('min_rating', '')
    if min_rating:
        try:
            places = places.filter(rating__gte=float(min_rating))
        except ValueError:
            pass
    
    # Verified filter
    verified_only = request.GET.get('verified', '')
    if verified_only == 'true':
        places = places.filter(is_verified=True)
    
    # Sorting
    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'rating':
        places = places.order_by('-rating', '-review_count')
    elif sort_by == 'name':
        places = places.order_by('name')
    elif sort_by == 'newest':
        places = places.order_by('-created_at')
    elif sort_by == 'reviews':
        places = places.order_by('-review_count', '-rating')
    elif sort_by == 'popular':
        places = places.annotate(
            popularity=Coalesce(Count('reviews'), 0) + Coalesce(Count('images'), 0)
        ).order_by('-popularity', '-rating')
    else:  # featured
        places = places.order_by('-is_featured', '-rating', 'name')
    
    # Pagination
    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(places, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get featured places for hero section
    featured_places = Place.objects.filter(is_active=True, is_featured=True).select_related('category')[:8]
    
    # Get trending places (high rating + recent reviews)
    trending_places = Place.objects.filter(
        is_active=True,
        rating__gte=4.0,
        review_count__gte=5
    ).order_by('-review_count', '-rating')[:6]
    
    # Get popular districts with counts
    popular_districts = Place.objects.filter(is_active=True).values('district').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Get top rated places
    top_rated = Place.objects.filter(is_active=True, rating__gte=4.5).order_by('-rating', '-review_count')[:4]
    
    # District choices for filter
    district_choices = Place.DISTRICT_CHOICES
    price_choices = Place.PRICE_RANGE_CHOICES
    
    # Statistics
    total_places = Place.objects.filter(is_active=True).count()
    avg_rating = Place.objects.filter(is_active=True).aggregate(Avg('rating'))['rating__avg'] or 0
    total_reviews = Place.objects.filter(is_active=True).aggregate(
        total=Coalesce(Count('reviews'), 0)
    )['total'] or 0
    
    # Get favorited place IDs for current user
    favorited_place_ids = set()
    if request.user.is_authenticated:
        favorited_place_ids = set(PlaceFavorite.objects.filter(
            user=request.user
        ).values_list('place_id', flat=True))
    
    context = {
        'page_obj': page_obj,
        'places': page_obj.object_list,
        'categories': categories,
        'featured_places': featured_places,
        'trending_places': trending_places,
        'top_rated': top_rated,
        'popular_districts': popular_districts,
        'district_choices': district_choices,
        'price_choices': price_choices,
        'search_query': search_query,
        'category_filter': category_filter,
        'district_filter': district_filter,
        'price_filter': price_filter,
        'min_rating': min_rating,
        'verified_only': verified_only,
        'sort_by': sort_by,
        'per_page': per_page,
        'total_count': paginator.count,
        'total_places': total_places,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
        'favorited_place_ids': favorited_place_ids,
    }
    
    return render(request, 'core/places.html', context)


def place_detail(request, pk):
    """View for displaying detailed information about a specific place"""
    place = get_object_or_404(Place, pk=pk, is_active=True)
    
    # Handle review submission
    if request.method == 'POST':
        from .models import PlaceReview
        from django.contrib import messages
        
        reviewer_name = request.POST.get('reviewer_name', '').strip()
        reviewer_email = request.POST.get('reviewer_email', '').strip()
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        
        if reviewer_name and rating and comment:
            try:
                rating = int(rating)
                if 1 <= rating <= 5:
                    # Check if review already exists for this email
                    if reviewer_email:
                        existing_review = PlaceReview.objects.filter(
                            place=place,
                            reviewer_email=reviewer_email
                        ).first()
                        if existing_review:
                            messages.warning(request, 'Bu email ünvanı ilə artıq rəy göndərilmişdir.')
                        else:
                            review = PlaceReview.objects.create(
                                place=place,
                                reviewer_name=reviewer_name,
                                reviewer_email=reviewer_email if reviewer_email else None,
                                rating=rating,
                                comment=comment,
                                is_approved=False  # Requires admin approval
                            )
                            messages.success(request, 'Rəyiniz göndərildi! Təsdiqləndikdən sonra göstəriləcək.')
                    else:
                        # Create review without email check if no email provided
                        review = PlaceReview.objects.create(
                            place=place,
                            reviewer_name=reviewer_name,
                            reviewer_email=None,
                            rating=rating,
                            comment=comment,
                            is_approved=False
                        )
                        messages.success(request, 'Rəyiniz göndərildi! Təsdiqləndikdən sonra göstəriləcək.')
                    
                    # Recalculate place rating
                    from django.db.models import Avg
                    approved_reviews = place.reviews.filter(is_approved=True)
                    if approved_reviews.exists():
                        avg_rating = approved_reviews.aggregate(Avg('rating'))['rating__avg']
                        place.rating = round(avg_rating, 2)
                        place.review_count = approved_reviews.count()
                        place.save()
            except (ValueError, TypeError):
                messages.error(request, 'Xəta baş verdi. Zəhmət olmasa yenidən cəhd edin.')
        else:
            messages.error(request, 'Zəhmət olmasa bütün məlumatları doldurun.')
    
    # Get approved reviews
    reviews = place.reviews.filter(is_approved=True).order_by('-created_at')[:10]
    
    # Get related places from same category
    related_places = Place.objects.filter(
        category=place.category,
        is_active=True
    ).exclude(pk=place.pk)[:4]
    
    # Check if place is favorited by current user
    is_favorited = False
    favorited_place_ids = set()
    if request.user.is_authenticated:
        is_favorited = PlaceFavorite.objects.filter(
            user=request.user,
            place=place
        ).exists()
        favorited_place_ids = set(PlaceFavorite.objects.filter(
            user=request.user
        ).values_list('place_id', flat=True))
    
    context = {
        'place': place,
        'reviews': reviews,
        'related_places': related_places,
        'is_favorited': is_favorited,
        'favorited_place_ids': favorited_place_ids,
        'page_title': f"{place.name} - Acteezer",
    }
    
    return render(request, 'core/place_detail.html', context)


@login_required
def liked_places(request):
    """View for displaying user's liked/favorite places"""
    # Get all places favorited by the current user
    favorite_place_ids = PlaceFavorite.objects.filter(
        user=request.user
    ).values_list('place_id', flat=True)
    
    places = Place.objects.filter(
        id__in=favorite_place_ids,
        is_active=True
    ).select_related('category').prefetch_related('images', 'reviews')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        places = places.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Category filter
    category_filter = request.GET.get('category', '')
    if category_filter:
        places = places.filter(category__category_type=category_filter)
    
    # District filter
    district_filter = request.GET.get('district', '')
    if district_filter:
        places = places.filter(district=district_filter)
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'rating':
        places = places.order_by('-rating', '-review_count')
    elif sort_by == 'name':
        places = places.order_by('name')
    elif sort_by == 'reviews':
        places = places.order_by('-review_count', '-rating')
    else:  # newest (default for favorites)
        # Order by when they were favorited (most recent first)
        # Get favorite IDs ordered by creation date
        favorite_ids_ordered = list(PlaceFavorite.objects.filter(
            user=request.user
        ).order_by('-created_at').values_list('place_id', flat=True))
        
        # Preserve the order of favorites
        if favorite_ids_ordered:
            preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(favorite_ids_ordered)])
            places = places.filter(id__in=favorite_ids_ordered).order_by(preserved)
        else:
            places = places.none()
    
    # Pagination
    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(places, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = PlaceCategory.objects.all().order_by('name')
    
    # District choices for filter
    district_choices = Place.DISTRICT_CHOICES
    
    # Get total count
    total_favorites = PlaceFavorite.objects.filter(user=request.user).count()
    
    context = {
        'page_obj': page_obj,
        'places': page_obj.object_list,
        'categories': categories,
        'district_choices': district_choices,
        'search_query': search_query,
        'category_filter': category_filter,
        'district_filter': district_filter,
        'sort_by': sort_by,
        'per_page': per_page,
        'total_count': paginator.count,
        'total_favorites': total_favorites,
    }
    
    return render(request, 'places/liked_places.html', context)


@login_required
@require_POST
def toggle_favorite(request, pk):
    """Toggle favorite status for a place"""
    place = get_object_or_404(Place, pk=pk, is_active=True)
    
    favorite, created = PlaceFavorite.objects.get_or_create(
        user=request.user,
        place=place
    )
    
    if not created:
        # Already favorited, remove it
        favorite.delete()
        is_favorited = False
        message = 'Məkan bəyənməklərdən çıxarıldı'
    else:
        # Newly favorited
        is_favorited = True
        message = 'Məkan bəyənməklərə əlavə edildi'
    
    return JsonResponse({
        'success': True,
        'is_favorited': is_favorited,
        'message': message
    })