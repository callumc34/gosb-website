from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import template
from CCG_Functions.cardCreation import getBasicCard, DB_DIR, NUM_CARDS
from api.templatetags import apiFunctions
from math import ceil
import os, os.path, sqlite3

"""SEARCH_VALUES = {
	"ID" : None,
	"cardSet" : None,
	"cardName" : None,
	"description" : None,
	"cardType" : None, 
	"cardType1" : None,
	"cardType2" : None,
	"rarityId" : None,
	"apectId" : None,
	"collectorNumber" : None,
	"teamId" : None,
	"attValueMin" : None,
	"attValueMax" : None,
	"defValueMin" : None,
	"defValueMax" : None,
	"spdValueMin" : None,
	"spdValueMax" : None,
	"heaValueMin" : None,
	"heaValueMax" : None,
	"tpValueMin" : None,
	"tpValueMax" : None,
	"titanBirth" : None
}
"""

def index(request):
	page = int(request.GET.get('page', 1)) - 1
	if page < 0:
		page = 0
	context = BASE_CONTEXT
	context["CURRENT_PAGE"] = page + 1
	if request.GET:
		cards = apiFunctions.advancedSearch(request)
		context["SEARCHED"] = True
	else:
		cards = None
		context["SEARCHED"] = False
	if cards:
		context['TOTAL_PAGES'] = range(1, ceil(len(cards)/50) + 1)
		context["DISPLAY_CARDS"] = [cards[i] for i in getRangeCards(page, len(cards))]
		context["TOTAL_CARDS"] = len(cards)
		context["LAST_PAGE"] = ceil(len(cards)/50)
	else:
		context["FOUND_CARDS"] = None
		context['TOTAL_PAGES'] = None
		context["DISPLAY_CARDS"] = None
		context["TOTAL_CARDS"] = 0
		context["LAST_PAGE"] = 0
	print(context["CURRENT_PAGE"], context["TOTAL_PAGES"])
	return render(request, "static/Search/core.html", context)


def getBaseContext():	
	conn = sqlite3.connect(DB_DIR)
	c = conn.cursor()
	context = {
		'NUM_CARDS' : NUM_CARDS,
		'sets' : [i[0] for i in c.execute("SELECT SetName FROM tlkpSets;")],
		'cardTypes' : [i[0] for i in c.execute("SELECT CardTypeName from tlkpCardType;")],
		'types' : [i[0] for i in c.execute("SELECT TypeName FROM tlkpType;").fetchall()],
		'raritys' : [i[0] for i in c.execute("SELECT RarityName FROM tlkpRarity").fetchall()],
		'aspects' : [i[0] for i in c.execute("SELECT AspectName FROM tlkpAspects;").fetchall()],
		'collectorRanges' : c.execute("SELECT MIN(CollectorNumber), MAX(CollectorNumber) FROM tblBasicCards;").fetchall()[0],
		'teams' : [i[0] for i in c.execute("SELECT TeamName FROM tlkpTeams;").fetchall()],
		'attRanges' : c.execute("SELECT MIN(Attack), MAX(Attack) FROM tblBasicCards;").fetchall()[0],
		'defRanges' : c.execute("SELECT MIN(Defence), MAX(Defence) FROM tblBasicCards;").fetchall()[0],
		'spdRanges' : c.execute("SELECT MIN(Speed), MAX(Speed) FROM tblBasicCards;").fetchall()[0],
		'heaRanges' : c.execute("SELECT MIN(Health), MAX(Health) FROM tblBasicCards;").fetchall()[0],
		'tpRanges' : c.execute("SELECT MIN(TotalPoints), MAX(TotalPoints) FROM tblBasicCards;").fetchall()[0],
		'titanBirths' : [i[0] for i in c.execute("SELECT TitanBirthName FROM tlkpTitanBirth;").fetchall()],
		'permFXs' : [i[0] for i in c.execute("SELECT PermFXName FROM tlkpPermFX;").fetchall()]
	}
	return context

def getRangeCards(page, length):
	if length == 0:
		return 0
	elif (page * 50) > length:
		return range(length-2, length-1)
	elif ((page + 1)* 50) > length:
		return range(page * 50, length)
	else:
		return range(page * 50, (page + 1) * 50)

BASE_CONTEXT = getBaseContext()