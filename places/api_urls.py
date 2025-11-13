from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    PlaceCategoryViewSet, PlaceViewSet,
    PlaceReviewViewSet, PlaceFavoriteViewSet
)

router = DefaultRouter()
router.register(r'categories', PlaceCategoryViewSet, basename='place-category')
router.register(r'places', PlaceViewSet, basename='place')
router.register(r'reviews', PlaceReviewViewSet, basename='place-review')
router.register(r'favorites', PlaceFavoriteViewSet, basename='place-favorite')

urlpatterns = [
    path('', include(router.urls)),
]

