from django.urls import path
from quizzApp import views

urlpatterns = [
    path('api/text/summarize', views.text),
]