from django.urls import path
from . import views

urlpatterns = [
    path('', views.roster_view, name='Roster'),
    path('<int:id>', views.performer_availability_view, name='Roster'),
]
