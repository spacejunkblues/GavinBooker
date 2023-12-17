from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='AdminDash'),
    path('userdetail/<int:r_id>/<int:id>', views.userdetail_view, name='UserDetail'),
]
