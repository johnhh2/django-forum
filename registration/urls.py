from django.conf.urls import url
from django.contrib.auth import views as auth_views
from .views import SignUpView, LogInView, PasswordResetView, PasswordResetSuccessView

app_name = 'registration'
urlpatterns = [
    url(r'login/', LogInView, name='login'),
    url(r'logout/', auth_views.logout, name='logout'),
    url(r'signup/', SignUpView, name='signup'),
    url(r'password_reset/', PasswordResetView, name='password_reset'),
    url(r'password_reset_success/', PasswordResetSuccessView, name='password_reset_success'), 
]   
