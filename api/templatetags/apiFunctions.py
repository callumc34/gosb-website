from django import template
from django.http import HttpResponse
from django.shortcuts import render, redirect
from CCG_Functions.cardCreation import *
from CCG_Functions.deckMaker import BasicDeck
from DeckMaker import models as DeckModels
from ast import literal_eval
import os, os.path
import sqlite3
import json
import datetime
import requests

DECKS_KEY = "" #Key to access the deck cloud storage
DECKS_WEB = "" #Location of decks cloud storage

"""Custom exception"""

class CloudError(Exception):
	pass

""" Tags and api functions"""

register = template.Library()

@register.filter
def isSwarm(ID):
	"""
	Check if a given ID has swarm ability
	"""
	conn = sqlite3.connect(DB_DIR)
	c = conn.cursor()
	if c.execute(
		"SELECT PermFXID FROM tblBasicCards WHERE BasicCardID = ?;", (ID,)).fetchone()[0] == 67:
		return True
	else:
		return False

@register.simple_tag
def idToName(request, ID=None, idType=None):
	"""
	ID Types:
	ID - Basic card ID
	set - Card set
	PermFX - Card's ability
	CardType - Card type
	rarity - Card rarity
	aspect - card aspect
	team - Card's team
	titanBirth - titan birth of card
	type - Type1/2 of card
	"""
	if request:
		ID = request.GET.get("ID", None)
		idType = request.GET.get("type", None)
	print(ID)
	if not ID and ID != 0:
		raise AttributeError(f"Missing arguments request = {request}, ID = {ID}, IDType = {idType}")

	conn = sqlite3.connect(DB_DIR)
	c = conn.cursor() 
	returnValue = False
	if idType == "ID":
		returnValue = c.execute("SELECT BasicCardName FROM tblBasicCards WHERE BasicCardId = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "set":
		returnValue = c.execute("SELECT SetName FROM tlkpSets WHERE SetID = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "PermFX":
		returnValue = c.execute("SELECT PermFXName FROM tlkpPermFX WHERE PermFXID = ?;",
			 (ID,)).fetchall()[0][0]
	elif idType == "CardType":
		returnValue = c.execute("SELECT CardTypeName FROM tlkpCardType WHERE CardTypeID = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "rarity":
		returnValue = c.execute("SELECT RarityName FROM tlkpRarity WHERE RarityID = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "aspect":
		returnValue = c.execute("SELECT AspectName FROM tlkpAspects WHERE AspectID = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "team":
		returnValue = c.execute("SELECT TeamName FROM tlkpTeams WHERE TeamID = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "titanBirth":
		returnValue = c.execute("SELECT TitanBirthName FROM tlkpTitanBirth WHERE TitanBirthID = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "type":
		returnValue = c.execute("SELECT TypeName FROM tlkpType WHERE TypeID = ?;",
		 (ID,)).fetchall()[0][0]
	else:
		pass

	if returnValue:
		return returnValue
	else:
		return "No name available."

@register.simple_tag
def idToDescription(request, ID=None, idType=None):
	"""
	ID Types:
	ID - Basic card ID
	set - Card set
	PermFX - Card's ability
	CardType - Card type
	rarity - Card rarity
	aspect - card aspect
	team - Card's team
	titanBirth - titan birth of card
	type - Type1/2 of card
	"""
	if request:
		ID = request.GET.get("ID", None)
		idType = request.GET.get("type", None)
	if not ID and ID != 0:
		raise AttributeError(f"Missing arguments request = {request}, ID = {ID}, IDType = {idType}")

	conn = sqlite3.connect(DB_DIR)
	c = conn.cursor()
	returnValue = False
	if idType == "ID":
		returnValue = c.execute("SELECT BasicCardDescription FROM tblBasicCards WHERE BasicCardId = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "set":
		returnValue = c.execute("SELECT SetDescription FROM tlkpSets WHERE SetID = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "PermFX":
		returnValue = c.execute("SELECT PermFXDescription FROM tlkpPermFX WHERE PermFXID = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "CardType":
		returnValue = c.execute("SELECT CardTypeDescription FROM tlkpCardType WHERE CardTypeID = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "rarity":
		returnValue = c.execute("SELECT RarityDescription FROM tlkpRarity WHERE RarityID = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "aspect":
		returnValue = c.execute("SELECT AspectDescription FROM tlkpAspects WHERE AspectID = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "team":
		returnValue = c.execute("SELECT TeamDescription FROM tlkpTeams WHERE TeamID = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "titanBirth":
		returnValue = c.execute("SELECT TitanBirthDescription FROM tlkpTitanBirth WHERE TitanBirthID = ?;",
		 (ID,)).fetchall()[0][0]
	elif idType == "type":
		returnValue = c.execute("SELECT TypeDescription FROM tlkpType WHERE TypeID = ?;",
		 (ID,)).fetchall()[0][0]
	else:
		pass

	if returnValue:
		return returnValue
	else:
		return "No description available."

#No Filter
def getCardJSON(ID):
	return json.dumps(getBasicCard(ID).__dict__)

#No Filter
def getCardImage(request, ID=None):
	if request:
		ID = request.GET.get("ID", None)
	if not ID:
		raise AttributeError(f"Missing arguments request = {request}, ID = {ID}")
	image = createCardImage(ALL_CARDS[ID])
	response = HttpResponse(content_type="image/png")
	image.save(response, "PNG")
	return response


#No Filter
def advancedSearch(request, querys=None):
	if request:
		search = request.GET
	if not search:
		raise AttributeError(f"Missing arguments request = {request}, querys = {querys}")
	conn = sqlite3.connect(DB_DIR)
	c = conn.cursor()
	statements = []
	for opt, value in search.items():
		try:
			if opt == "ID":
				value = int(value)
				statements.append(f"BasicCardId = {value}")
			elif opt == "cardSet":
				sID = int(c.execute("SELECT SetID FROM tlkpSets WHERE SetName = ?;", (value,)).fetchall()[0][0])
				statements.append(f"SetID = {sID}")
			elif opt == "cardName":
				s = (f"%{value}%", )
				name = c.execute("SELECT BasicCardName FROM tblBasicCards WHERE BasicCardName LIKE ?;", s).fetchall()[0][0]
				statements.append(f"BasicCardName = '{name}'")
			elif opt =="description":				
				s = (f"%{value}%", )
				name = c.execute("SELECT BasicCardDescription FROM tblBasicCards WHERE BasicCardDescription LIKE ?;", s).fetchall()[0][0]
				statements.append(f"BasicCardDescription = '{value}'")
			elif opt == "abilityType":
				aT = int(c.execute("SELECT PermFXID FROM tlkpPermFX WHERE PermFXName = ?;", (value,)).fetchall()[0][0])
				statements.append(f"PermFXID = {aT}")
			elif opt == "cardType":
				cT = int(c.execute("SELECT CardTypeID FROM tlkpCardType WHERE CardTypeName = ?;", (value,)).fetchall()[0][0])
				statements.append(f"cardTypeID = {cT}")
			elif opt == "cardType1":
				cT1 = int(c.execute("SELECT TypeID FROM tlkpType WHERE TypeName = ?;", (value,)).fetchall()[0][0])
				statements.append(f"TypeID = {cT1}")
			elif opt == "cardType2":
				cT2 = int(c.execute("SELECT TypeID FROM tlkpType WHERE TypeName = ?;", (value,)).fetchall()[0][0])
				statements.append(f"Type2ID = {cT2}")
			elif opt == "rarityId":
				rId = int(c.execute("SELECT RarityID FROM tlkpRarity WHERE RarityName = ?;", (value,)).fetchall()[0][0])
				statements.append(f"RarityID = {rId}")
			elif opt == "aspectId":
				aId = int(c.execute("SELECT AspectID FROM tlkpAspects WHERE AspectName = ?;", (value, )).fetchall()[0][0])
				statements.append(f"AspectID = {aId}")
			elif opt == "collectorNumber":
				value = int(value)
				statements.append(f"CollectorNumber = {value}")
			elif opt == "teamId":
				tId = int(c.execute("SELECT TeamID FROM tlkpTeams WHERE TeamName = ?;", (value, )).fetchall()[0][0])
				statements.append(f"TeamID = {tId}")
			elif opt == "attValueMin":
				value = int(value)
				statements.append(f"Attack > {value}")
			elif opt == "attValueMax":
				value = int(value)
				statements.append(f"Attack < {value}")
			elif opt == "defValueMin":
				value = int(value)
				statements.append(f"Defence > {value}")
			elif opt == "defValueMax":
				value = int(value)
				statements.append(f"Defence < {value}")
			elif opt == "spdValueMin":
				value = int(value)
				statements.append(f"Speed > {value}")
			elif opt == "spdValueMax":
				value = int(value)
				statements.append(f"Speed < {value}")
			elif opt == "heaValueMin":
				value = int(value)
				statements.append(f"Health > {value}")
			elif opt == "heaValueMax":
				value = int(value)
				statements.append(f"Health < {value}")
			elif opt == "tpValueMin":
				value = int(value)
				statements.append(f"TotalPoints > {value}")
			elif opt == "tpValueMax":
				value = int(value)
				statements.append(f"TotalPoints < {value}")
			elif opt == "titanBirth":
				tB = int(c.execute("SELECT TitanBirthID FROM tlkpTitanBirth WHERE TitanBirthName = ?;",
				 (value,)).fetchall()[0][0])
				statements.append(f"TitanBirthID = {tB}")
			elif opt == "idValueMin":
				rM = int(value)
				statements.append(f"BasicCardID > {rM}")
			elif opt == "idValueMax":
				rM = int(value)
				statements.append(f"BasicCardID < {rM}")
			else:
				pass
		except Exception as e:
			print(e)
			print("Invalid args: " + str(search))
			return None
	if not statements:
		return None
	statement =  " AND ".join(statements)
	cards = c.execute(f"SELECT * FROM tblBasicCards WHERE {statement};").fetchall()
	if cards:
		return [getBasicCard(i[0]) for i in cards]
	else:
		return None


"""Decks"""

#No filter
def filterDecks(request, fromApi=True):
	owner = request.GET.get("owner", None)
	deckName = request.GET.get("deckName", None)
	deckDate = request.GET.get("date", None)
	if owner or deckName or deckDate:
		decks = DeckModels.deck.objects.all()
		if owner:
			decks = decks.filter(DeckOwner__icontains=owner)
		if deckName:
			decks = decks.filter(DeckName__icontains=deckName)
		if deckDate:
			decks = decks.filter(DeckDate__date=deckDate)

		deckDict = {"decks" : list(decks.values())}
		if fromApi:
			return HttpResponse(
				json.dumps(deckDict, default=str), content_type="text/json")
		else:
			return deckDict["decks"]

	else:
		if fromApi:
			return HttpResponse('{"Error" : "No arguments given"}')
		else:
			return None
#No filter
def createDeck(request):
	deck = literal_eval(request.GET.get("deck", "None"))
	redirectAfter = bool(request.GET.get("redirect", "True").title)
	if not deck:
		#add a deck failed page
		if redirect:
			return redirect("/deck/edit", permanent=True)
		else:
			return HttpResponse("No deck supplied")

	deckId = DeckModels.MaxID() #Get the next available ID
	if deckId:
		#Check that there are other decks before it
		deckId += 1
	else:
		deckId = 1

	#Check Tags
	tags = {}
	Owner = request.GET.get("Owner", "No owner")
	if Owner == "":
		Owner = "No owner"
	tags["owner"] = Owner
	deckName = request.GET.get("DeckName", "No deck name")
	if deckName == "":
		deckName = "No deck name"
	tags["deckname"] = deckName
	tags["date"] = str(datetime.datetime.now())[:10]

	newDeck = BasicDeck(f"/tmp/tempDecks/deck{deckId}.sbd", **tags) #New deck instance
	newDeck.dictToDeck(deck) #Add the passed dictionary to the deck

	#Validate and write the deck to a the file
	try:
		newDeck.writeDeck()
	except Exception as e:
		return HttpResponse(f"Error writing deck to file - Error: {e}")

	r = requests.post(DECKS_WEB + "upload/", data={
			"ID": deckId,
			"idKey" : DECKS_KEY
		}, files={"fileData" : open(f"/tmp/tempDecks/deck{deckId}.sbd", "rb")})
	if r.ok:
		pass

	else:
		raise CloudError(f"Could not upload file - ID : {deckId}\nResponse - {r.text}")

	# conn = sqlite3.connect(DECKS_DB)
	# c = conn.cursor()
	# c.execute(
	# 	"INSERT INTO tblDecks (DeckId, DeckName, DeckOwner, DeckDate) VALUES (?, ?, ?, ?);",
	# 	(deckId, tags["owner"], tags["deckname"], tags["date"]))
	# conn.commit()
	# conn.close()
	newDbDeck = DeckModels.deck(DeckId=deckId, DeckName=tags["deckname"],
		DeckOwner=tags["owner"], DeckDate=tags["date"])
	newDbDeck.save()
	if redirect:
		return redirect("/deck/show/?ID=" + str(deckId), permanent=True)
	else:
		return HttpResponse("Deck upload successful")

#No filter
def fetchDeckText(request, ID=None):
	if request:
		ID = request.GET.get("ID", None)
	if not ID:
		raise AttributeError(f"Missing arguments request = {request}, ID = {ID}")

	r = requests.post(DECKS_WEB + "getDeck/", data={"ID" : ID, "idKey" : DECKS_KEY})
	if r.ok:
		return r.text

	else:
		raise CloudError(f"Could not download file - ID : {ID}\nResponse - {r.text}")
	

@register.simple_tag
def returnDeck(ID):
	tmpDeckFile = f"/tmp/tempDecks/deck{ID}.sbd"
	with open(tmpDeckFile, "w") as deckF:
		deckF.write(fetchDeckText(None, ID))
	deck = BasicDeck(tmpDeckFile)
	try:
		deck.parseDeck()
		return None, deck
	except Exception as e:
		return "Could not parse deck error: " + str(e), False

