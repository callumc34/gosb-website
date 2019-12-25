from django.shortcuts import render
from django.http import HttpResponse
from .templatetags import apiFunctions
import json

def index(request):
	return HttpResponse(
		"<h1>Documentation still under construction check source code or message a web dev on discord</h1>")

def card(request):
	ID = request.GET.get("ID", None)
	if not ID:
		return
	return HttpResponse(apiFunctions.getCardJSON(ID), content_type="text/JSON")

def cardSearch(request):
	if not request.GET:
		return HttpResponse('{ "Error" : "request could not be parsed correctly, check your get request"')
	else:
		cards = apiFunctions.advancedSearch(request)
		if cards:
			cardsJson = {"Cards" : []}
			for i in cards:
				cardsJson["Cards"].append(i.__dict__)
			return HttpResponse(json.dumps(cardsJson), content_type="text/JSON")
		else:
			return HttpResponse('{ "Error" : "No cards found" }', content_type="text/JSON")

def uploadDeck(request):
	return apiFunctions.createDeck(request)

def getDeck(request):
	ID = request.GET.get("ID", None)
	if not ID:
		return HttpResponse("{'ERROR' : 'No ID given'}", content_type="text/JSON")
	Error, deck = apiFunctions.returnDeck(ID)
	if not Error:
		return HttpResponse(json.dumps(deck.json()), content_type="text/JSON")
	else:
		return HttpResponse(f"{'ERROR' : {Error}}", content_type="text/JSON")

def deckText(request):
	return HttpResponse(apiFunctions.fetchDeckText(request), content_type="text/plain")

def searchDecks(request):
	return apiFunctions.filterDecks(request)