from django.urls import path
from . import views

urlpatterns = [
    path('', views.profilestatus_view, name='Metrics'),
    path('visits/<int:year>/<int:month>', views.visits_view, name='Metrics'),
    path('gigs/<int:year>/<int:month>', views.gigs_view, name='Gigs'),
    path('profile/<int:year>/<int:month>', views.profilestatus_view, name='Profile'),
    path('problem', views.report_problem, name='Problem'),
]
