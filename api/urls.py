from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name="apiDocs"),
	path('card/', views.card, name="cardJSON"),
	path('decks/create/', views.uploadDeck, name="uploadDeck"),
	path('decks/fetch/', views.getDeck, name="getDeck"),
	path('decks/text/', views.deckText, name="deckText"),
	path('decks/search/', views.searchDecks, name="searchDecks"),
	path('cardSearch/', views.cardSearch, name="cardSearchJSON")
]