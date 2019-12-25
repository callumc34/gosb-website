from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from . import views

urlpatterns = [
	path('', views.search),
	path('edit/', views.deckMaker, name="deckMaker"),
	path("show/", views.showDeck, name="showDeck")
]