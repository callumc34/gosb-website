from django.shortcuts import render
from CCG_Functions.cardCreation import getBasicCard

# Create your views here.

def index(request):
	context = {}
	cardId = request.GET.get("ID", None)
	if not cardId:
		pass
	else:
		context["CARD"] = getBasicCard(cardId)
	return render(request, "static/ViewCard/core.html", context)

