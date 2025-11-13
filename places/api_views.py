from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import PlaceCategory, Place, PlaceImage, PlaceReview, PlaceFavorite
from .serializers import (
    PlaceCategorySerializer, PlaceListSerializer, PlaceDetailSerializer,
    PlaceReviewSerializer, PlaceFavoriteSerializer
)


class PlaceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for place categories"""
    queryset = PlaceCategory.objects.all()
    serializer_class = PlaceCategorySerializer
    permission_classes = [permissions.AllowAny]


class PlaceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for places"""
    queryset = Place.objects.filter(is_active=True)
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PlaceDetailSerializer
        return PlaceListSerializer
    
    def get_queryset(self):
        queryset = Place.objects.filter(is_active=True)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(short_description__icontains=search) |
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
        
        # Price range filter
        price = self.request.query_params.get('price', None)
        if price:
            queryset = queryset.filter(price_range=price)
        
        # Rating filter
        min_rating = self.request.query_params.get('min_rating', None)
        if min_rating:
            try:
                queryset = queryset.filter(rating__gte=float(min_rating))
            except ValueError:
                pass
        
        # Verified filter
        verified = self.request.query_params.get('verified', None)
        if verified == 'true':
            queryset = queryset.filter(is_verified=True)
        
        # Sorting
        sort_by = self.request.query_params.get('sort', 'featured')
        if sort_by == 'rating':
            queryset = queryset.order_by('-rating', '-review_count')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'reviews':
            queryset = queryset.order_by('-review_count', '-rating')
        else:  # featured
            queryset = queryset.order_by('-is_featured', '-rating', 'name')
        
        return queryset.select_related('category').prefetch_related('images', 'reviews')
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def is_favorited(self, request, pk=None):
        """Check if place is favorited by current user"""
        place = self.get_object()
        is_favorited = PlaceFavorite.objects.filter(
            user=request.user,
            place=place
        ).exists()
        
        return Response({'is_favorited': is_favorited})
    
    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        """Toggle favorite status"""
        place = self.get_object()
        
        if request.method == 'POST':
            favorite, created = PlaceFavorite.objects.get_or_create(
                user=request.user,
                place=place
            )
            if created:
                return Response({
                    'success': True,
                    'is_favorited': True,
                    'message': 'Place added to favorites'
                })
            else:
                return Response({
                    'success': True,
                    'is_favorited': True,
                    'message': 'Place already in favorites'
                })
        else:  # DELETE
            try:
                favorite = PlaceFavorite.objects.get(
                    user=request.user,
                    place=place
                )
                favorite.delete()
                return Response({
                    'success': True,
                    'is_favorited': False,
                    'message': 'Place removed from favorites'
                })
            except PlaceFavorite.DoesNotExist:
                return Response({
                    'success': False,
                    'is_favorited': False,
                    'message': 'Place not in favorites'
                }, status=status.HTTP_404_NOT_FOUND)


class PlaceReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for place reviews"""
    queryset = PlaceReview.objects.filter(is_approved=True)
    serializer_class = PlaceReviewSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        place_id = self.request.query_params.get('place', None)
        if place_id:
            return PlaceReview.objects.filter(place_id=place_id, is_approved=True)
        return PlaceReview.objects.filter(is_approved=True)
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]  # Anyone can create review
        return [permissions.AllowAny()]


class PlaceFavoriteViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user's favorite places"""
    queryset = PlaceFavorite.objects.all()
    serializer_class = PlaceFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PlaceFavorite.objects.filter(user=self.request.user).select_related('place')

