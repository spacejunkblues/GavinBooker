from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='Calendar'),
    path('<int:year>/<int:month>', views.calendar_view, name='Calendar'),
    path('detail/<int:id>', views.detail_view, name='Detail'),
    path('add/<int:year>/<int:month>/<int:day>', views.add_availability_view, name='Availability'),
]
