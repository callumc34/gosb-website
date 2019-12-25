from django.shortcuts import render, redirect
from django.http import HttpResponse
from api.templatetags.apiFunctions import createDeck, returnDeck, filterDecks
from ccg_web.settings import BASE_DIR
from DeckMaker.models import MaxID
from CCG_Functions.cardCreation import ALL_CARDS, NUM_CARDS, DB_DIR
from CCG_Functions.deckMaker import BasicDeck, ParseError, DeckError
import sqlite3
import os.path

def search(request):
	context = {}
	if request.GET:
		context["DECKS"] = filterDecks(request, fromApi=False)
		context["SEARCHED"] = True

	else:
		context["DECKS"] = None
		context["SEARCHED"] = False
		
	return render(request, "static/DeckSearch/core.html", context)

def showDeck(request):
	deckId = int(request.GET.get("ID", None))
	maxDeckId = MaxID()
	if not deckId or deckId > maxDeckId or deckId < 0:
		return render(request, "ccg_web/templates/404.html", None)
	context = {"ID" : deckId}
	error, deck = returnDeck(deckId)
	if not deck:
		#Add error messages
		return render(request, "ccg_web/templates/500.html", {"ERROR" : error})
	if not deck.templateReady():
		return render(request, "ccg_web/templates/500.html",
		 {"ERROR" : "Could not make the deck ready for the page"})
	context["DECK"] = deck
	return render(request, "static/ShowDeck/core.html", context)
	

def deckMaker(request):
	context = searchFormContext()
	context["ALL_CARDS"] = ALL_CARDS
	context["FILE_ERROR"] = None
	context["DECK"] = None
	context["TAGS"] = None
	deckId = request.GET.get("ID", None)
	if deckId:
		error, deck = returnDeck(deckId)
		if error:
			context["FILE_ERROR"] = error

	if request.FILES:
		file = request.FILES["deckFile"]
		if file.size > 5120:
			context["FILE_ERROR"] = "Max file size exceeded"
		deckStr = ""
		try:
			for chunk in request.FILES["deckFile"].chunks():
				deckStr += chunk.decode("utf-8")
		except:
			context["FILE_ERROR"] = "Error decoding file"
		deck = BasicDeck(None)
		try:
			deck.parseDeck(deckString=deckStr)
		except Exception as e:
			if type(e) == ParseError:
				context["FILE_ERROR"] = "Error parsing deck: " + str(e)
			elif type(e) == AssertionError:
				context["FILE_ERROR"] = \
				"Assertion Error during parsing of deck. Please check your cards are in the right section."
			elif type(e) == DeckError:
				context["FILE_ERROR"] = "Deck Error: " + str(e)
			else: #Unknown error
				print(e)
				context["FILE_ERROR"] = "An unknown error occured while parsing your deck."

	if deck:
		if not deck.templateReady():
			return render(request, "ccg_web/templates/500.html",
			 {"ERROR" : "Error getting your deck ready. Please check with a web admin"})
		else:
			context["DECK"] = deck.deckDict
			context["TAGS"] = deck.attributes


	return render(request, "static/DeckMaker/core.html", context)

def downloadDeck(request):
	ID = request.GET.get("ID", None)
	if not ID:
		return redirect("/deck/", permanent=True)
	Error, deck = returnDeck()
	if Error:
		return render(request, "ccg_web/templates/500.html", {"Error" : error})
	if os.path.exists(f"/tmp/tempDecks/deck{ID}.sbd"):
		return

def searchFormContext():
	conn = sqlite3.connect(DB_DIR)
	c = conn.cursor()
	context = {
		'NUM_CARDS' : NUM_CARDS,
		'sets' : [i[0] for i in c.execute("SELECT SetName FROM tlkpSets;")],
		'cardTypes' : [i[0] for i in c.execute("SELECT CardTypeName from tlkpCardType;")],
		'types' : [i[0] for i in c.execute("SELECT TypeName FROM tlkpType;").fetchall()],
		'aspects' : [i[0] for i in c.execute("SELECT AspectName FROM tlkpAspects;").fetchall()],
		'teams' : [i[0] for i in c.execute("SELECT TeamName FROM tlkpTeams;").fetchall()],
		'titanBirths' : [i[0] for i in c.execute("SELECT TitanBirthName FROM tlkpTitanBirth;").fetchall()],
		'permFXs' : [i[0] for i in c.execute("SELECT PermFXName FROM tlkpPermFX;").fetchall()]
	}
	return context

def getDeckContext(deckStr):
	context = {}
