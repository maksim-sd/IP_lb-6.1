from django.contrib import admin
from django.urls import path
from .api import api
from . import views


urlpatterns = [
    path('', views.home),
    path('api/', api.urls),
]