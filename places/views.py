from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Place, PlaceCategory


def places_list(request):
    """View for displaying list of places with search and filtering functionality"""
    places = Place.objects.filter(is_active=True).select_related('category')
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
    
    # Sorting
    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'rating':
        places = places.order_by('-rating', '-review_count')
    elif sort_by == 'name':
        places = places.order_by('name')
    elif sort_by == 'newest':
        places = places.order_by('-created_at')
    else:  # featured
        places = places.order_by('-is_featured', '-rating', 'name')
    
    # Pagination
    paginator = Paginator(places, 20)  # Show 20 places per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get featured places for hero section
    featured_places = Place.objects.filter(is_active=True, is_featured=True)[:8]
    
    # District choices for filter
    district_choices = Place.DISTRICT_CHOICES
    price_choices = Place.PRICE_RANGE_CHOICES
    
    context = {
        'page_obj': page_obj,
        'places': page_obj.object_list,
        'categories': categories,
        'featured_places': featured_places,
        'district_choices': district_choices,
        'price_choices': price_choices,
        'search_query': search_query,
        'category_filter': category_filter,
        'district_filter': district_filter,
        'price_filter': price_filter,
        'sort_by': sort_by,
        'total_count': paginator.count,
    }
    
    return render(request, 'core/places.html', context)


def place_detail(request, pk):
    """View for displaying detailed information about a specific place"""
    place = get_object_or_404(Place, pk=pk, is_active=True)
    
    # Get approved reviews
    reviews = place.reviews.filter(is_approved=True).order_by('-created_at')[:10]
    
    # Get related places from same category
    related_places = Place.objects.filter(
        category=place.category,
        is_active=True
    ).exclude(pk=place.pk)[:4]
    
    context = {
        'place': place,
        'reviews': reviews,
        'related_places': related_places,
        'page_title': f"{place.name} - Acteezer",
    }
    
    return render(request, 'core/place_detail.html', context)


def places_list(request):
    """View for displaying list of places with search and filtering functionality"""
    places = Place.objects.filter(is_active=True).select_related('category')
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
    
    # Sorting
    sort_by = request.GET.get('sort', 'featured')
    if sort_by == 'rating':
        places = places.order_by('-rating', '-review_count')
    elif sort_by == 'name':
        places = places.order_by('name')
    elif sort_by == 'newest':
        places = places.order_by('-created_at')
    else:  # featured
        places = places.order_by('-is_featured', '-rating', 'name')
    
    # Pagination
    paginator = Paginator(places, 20)  # Show 20 places per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get featured places for hero section
    featured_places = Place.objects.filter(is_active=True, is_featured=True)[:8]
    
    # District choices for filter
    district_choices = Place.DISTRICT_CHOICES
    price_choices = Place.PRICE_RANGE_CHOICES
    
    context = {
        'page_obj': page_obj,
        'places': page_obj.object_list,
        'categories': categories,
        'featured_places': featured_places,
        'district_choices': district_choices,
        'price_choices': price_choices,
        'search_query': search_query,
        'category_filter': category_filter,
        'district_filter': district_filter,
        'price_filter': price_filter,
        'sort_by': sort_by,
        'total_count': paginator.count,
    }
    
    return render(request, 'core/places.html', context)


def place_detail(request, pk):
    """View for displaying detailed information about a specific place"""
    place = get_object_or_404(Place, pk=pk, is_active=True)
    
    # Get approved reviews
    reviews = place.reviews.filter(is_approved=True).order_by('-created_at')[:10]
    
    # Get related places from same category
    related_places = Place.objects.filter(
        category=place.category,
        is_active=True
    ).exclude(pk=place.pk)[:4]
    
    context = {
        'place': place,
        'reviews': reviews,
        'related_places': related_places,
        'page_title': f"{place.name} - Acteezer",
    }
    
    return render(request, 'core/place_detail.html', context)