from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import template
from CCG_Functions.cardCreation import ALL_CARDS, NUM_CARDS
from math import ceil, floor
from api.templatetags import apiFunctions
import os, os.path, sqlite3
# Create your views here.

def index(request):
	totalPages = ceil(NUM_CARDS/50) + 1
	cardRange = [int(request.GET.get('from', 0)), int(request.GET.get('to', 0))]
	if cardRange[0] <= 0:
		if cardRange[1] > 50:
			cardRange[0] = cardRange[1] - 50
		else:
			cardRange[0] = 1
	else:
		pass

	if cardRange[1] == 0:
		if cardRange[0] == 1:
			cardRange[1] = 50
		else:
			cardRange[1] = cardRange[0] + 50

	if cardRange[1] > NUM_CARDS:
		cardRange[1] = NUM_CARDS
	else:
		pass

	if cardRange[0] > NUM_CARDS:
		cardRange[0] = NUM_CARDS - 1
	else:
		pass

	if cardRange[0] > cardRange[1]:
		tMax = cardRange[0] #Max is first in list
		tMin = cardRange[1]
		cardRange[1] = tMax
		cardRange[0] = tMin
		
	context = {'ALL_CARDS' : allCardsInRange(
		cardRange[0], cardRange[1]), 'MIN_RANGE' : cardRange[0], 'MAX_RANGE' : cardRange[1]}
	context['TOTAL_PAGES'] = range(1, totalPages)
	context["CURRENT_PAGE"] = floor(cardRange[0] / 50) + 1
	baseRender = render(request, "static/Main/core.html", context)
	return baseRender

def returnPage(request):
	page = int(request.GET.get('page', 1)) - 1
	return redirect("/cards/?from={}&to={}".format(
		page*50, (page + 1) * 50))
	

def returnImage(request):
	return apiFunctions.getCardImage(None, request.GET.get('ID', None))

def returnHeader(request):
	return HttpResponse(open("static/Global/Header.html", "r").read())

def allCardsInRange(min, max):
	v = []
	for i in range(min, max):
		v.append(ALL_CARDS[str(i)])

	return v