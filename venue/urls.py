from django.urls import path
from . import views

urlpatterns = [
    path('', views.venue_view, name='Venue'),
    path('create/', views.createvenue_view, name='CreateVenue'),
    path('activate/<int:id>', views.activatevenue_view, name='ActivateVenue'),
]
