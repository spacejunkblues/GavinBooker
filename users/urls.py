from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='Users'),
    path('login_user/', views.login_view, name='Login'),
    path('logout_user/', views.logout_view, name='Logout'),
    path('register_user/', views.register_view, name='Register'),
    path('activate/<uidb64>/<token>', views.activate_view, name='Activate'),
    path('passwordreset', views.passwordreset_view, name='ForgotPassword'),
    path('reset/<uidb64>/<token>', views.reset_view, name='Reset'),
    path('edit/', views.edit_view, name='Edit'),
    path('register_dummies/', views.register_dummy, name='Dummies'),
    path('delete_dummies/', views.delete_dummy, name='Dummies'),
]
