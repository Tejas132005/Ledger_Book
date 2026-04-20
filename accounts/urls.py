from django.urls import path
from .views import RegisterView, LoginView, ProfileUpdateView, logout_view

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile_update'),
    path('logout/', logout_view, name='logout'),
]
