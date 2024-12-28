from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('get_user_location/', views.get_user_location, name='get_user_location'),
    path('update_location/', views.update_location, name='update_location'),
    path('get-location-data/', views.get_location_data, name='get_location_data'),
    path('meeting-confirmation/', views.meeting_confirmation, name='meeting_confirmation'),
]
