from django.urls import path
from . import views
from . import chat_views

app_name = 'activities'

urlpatterns = [
    path('', views.activities_list, name='activities_list'),
    path('create/', views.create_activity, name='create_activity'),
    path('<int:pk>/', views.activity_detail, name='activity_detail'),
    path('<int:pk>/join/', views.join_activity, name='join_activity'),
    path('<int:pk>/cancel-join/', views.cancel_join_request, name='cancel_join_request'),
    path('<int:pk>/manage/<int:participant_id>/', views.manage_participant, name='manage_participant'),
    path('<int:pk>/delete/', views.delete_activity, name='delete_activity'),
    
    # Chat URLs
    path('<int:activity_id>/chat/messages/', chat_views.get_messages, name='get_messages'),
    path('<int:activity_id>/chat/send/', chat_views.send_message, name='send_message'),
    path('<int:activity_id>/chat/edit/<int:message_id>/', chat_views.edit_message, name='edit_message'),
    path('<int:activity_id>/chat/delete/<int:message_id>/', chat_views.delete_message, name='delete_message'),
]
