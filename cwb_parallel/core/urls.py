from django.conf import settings
from django.urls import path

from core import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('results/', views.ResultsView.as_view(), name='results'),
]
