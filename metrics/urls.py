from django.urls import path
from . import views

urlpatterns = [
    path('', views.metric_view, name='Metrics'),
    path('<int:year>/<int:month>', views.metric_view, name='Metrics'),
    path('gigs/<int:year>/<int:month>', views.gigs_view, name='Gigs'),
    path('profile/<int:year>/<int:month>', views.profilestatus_view, name='Profile'),
    path('problem', views.report_problem, name='Problem'),
]
