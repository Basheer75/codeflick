from django.urls import path
from . import views
from .views import hero_view, signup_view, login_view, dashboard_view, history_view, profile_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Hero / Landing Page
    path('', hero_view, name='hero'),

    # Authentication (all rendered through auth.html)
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='hero'), name='logout'),

    # Core App Pages
    path('home/', views.home, name='home'),
    path('questions/<str:level>/', views.question_list, name='question_list'),
    path('translate/<int:question_id>/', views.translate_view, name='translate'),
    path('load-question/', views.load_question_code, name='load_question_code'),

    # User Dash Pages
    path('dashboard/', dashboard_view, name='dashboard'),
    path('history/', history_view, name='history'),
    path('profile/', profile_view, name='profile'),
]
