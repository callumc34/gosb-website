from django.shortcuts import render, redirect
from django.http import HttpResponse
from django import template
from CCG_Functions.cardCreation import *
from math import ceil
import os, os.path, sqlite3

def index(request):
	context = {}
	return render(request, "static/Home/core.html", context)