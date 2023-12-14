from django.urls import path
from . import views

urlpatterns = [
    path('', views.roster_view, name='Roster'),
    path('<int:id>', views.performer_availability_view, name='Roster'),
    path('invite/', views.invite_view, name='Invite'),
    path('delete/<int:id>', views.delete_view, name='Delete'),
]
