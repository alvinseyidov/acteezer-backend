from django.urls import path
from . import views

app_name = 'places'

urlpatterns = [
    path('', views.places_list, name='places_list'),
    path('<int:pk>/', views.place_detail, name='place_detail'),
]

