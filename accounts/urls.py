from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('settings/', views.settings, name='settings'),
    path('user/<int:user_id>/', views.user_detail, name='user_detail'),
    path('my-activities/', views.my_activities, name='my_activities'),
    path('joined-activities/', views.joined_activities, name='joined_activities'),
    
    # People & Friends
    path('people/', views.people_list, name='people_list'),
    path('friends/', views.friends_list, name='friends_list'),
    path('friend-requests/', views.friend_requests, name='friend_requests'),
    path('send-friend-request/', views.send_friend_request, name='send_friend_request'),
    path('respond-friend-request/', views.respond_friend_request, name='respond_friend_request'),
    
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
