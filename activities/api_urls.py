from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    LanguageViewSet, ActivityCategoryViewSet, ActivityViewSet,
    ActivityCommentViewSet, ActivityMessageViewSet
)

router = DefaultRouter()
router.register(r'languages', LanguageViewSet, basename='language')
router.register(r'categories', ActivityCategoryViewSet, basename='activity-category')
router.register(r'activities', ActivityViewSet, basename='activity')
router.register(r'comments', ActivityCommentViewSet, basename='activity-comment')
router.register(r'messages', ActivityMessageViewSet, basename='activity-message')

urlpatterns = [
    path('', include(router.urls)),
]

