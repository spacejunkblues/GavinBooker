from django.urls import path
from . import views

urlpatterns = [
    path('', views.allbookings_view, name='Review'),
    path('<int:id>/', views.review_view, name='Review'),
    path('thanks/', views.thanks_view, name='Thanks'),
]
