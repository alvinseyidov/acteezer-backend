from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    LanguageViewSet, InterestViewSet, UserViewSet,
    FriendshipViewSet, BlogCategoryViewSet, BlogPostViewSet
)

router = DefaultRouter()
router.register(r'languages', LanguageViewSet, basename='language')
router.register(r'interests', InterestViewSet, basename='interest')
router.register(r'users', UserViewSet, basename='user')
router.register(r'friendships', FriendshipViewSet, basename='friendship')
router.register(r'blog-categories', BlogCategoryViewSet, basename='blog-category')
router.register(r'blog-posts', BlogPostViewSet, basename='blog-post')

urlpatterns = [
    path('', include(router.urls)),
]

