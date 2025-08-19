from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('my-activities/', views.my_activities, name='my_activities'),
    path('joined-activities/', views.joined_activities, name='joined_activities'),
    
    # Registration steps
    path('register/', views.phone_registration, name='phone_registration'),
    path('register/otp/', views.otp_verification, name='otp_verification'),
    path('register/name/', views.full_name_registration, name='full_name_registration'),
    path('register/languages/', views.languages_registration, name='languages_registration'),
    path('register/birthday/', views.birthday_registration, name='birthday_registration'),
    path('register/images/', views.images_registration, name='images_registration'),
    path('register/bio/', views.bio_registration, name='bio_registration'),
    path('register/interests/', views.interests_registration, name='interests_registration'),
    path('register/location/', views.location_registration, name='location_registration'),
    path('register/complete/', views.registration_complete, name='registration_complete'),
    
    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
