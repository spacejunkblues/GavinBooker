from django.urls import path
from . import views

urlpatterns = [
    path('', views.metric_view, name='Metrics'),
    path('problem', views.report_problem, name='Problem'),
]
