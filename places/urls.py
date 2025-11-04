from django.urls import path
from . import views

app_name = 'places'

urlpatterns = [
    path('', views.places_list, name='places_list'),
    path('liked/', views.liked_places, name='liked_places'),
    path('<int:pk>/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('<int:pk>/', views.place_detail, name='place_detail'),
]

