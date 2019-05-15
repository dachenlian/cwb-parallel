from django.conf import settings
from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('results/', views.ConcordanceView.as_view(), name='concordance'),
    path('translate/', views.TranslationView.as_view(), name='translation')
]
