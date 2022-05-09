from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('signin', views.signin, name='signinpage'),
    path('logout', views.logoutUser, name='logout'),
    path('forgetpass', views.forgetpass, name='pass'),
    path('index', views.index, name='home'),
    path('profile', views.profile, name='profile'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('admin_login/', views.admin_login, name="admin_login"),
    path('signup', views.signup, name='signuppage')
]
