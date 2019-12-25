from .cardCreation import BasicCardInstance, getBasicCard, DB_DIR
import re
import sqlite3
import datetime

class ParseError(Exception):
	pass

class DeckError(Exception):
	pass

class BasicDeck:
	"""
	Assign a file and attributes to a BasicDeck
	"""
	def __init__(self, file, **kwargs):
		"""
		Initialise the BasicDeck with the location to be stored
		Any additional arguments fill the attributes dictionary
		"""
		self.file = file
		self._deck = {}
		self.attributes = kwargs

	def __str__(self):
		deckString = ""
		for attr, val in self.attributes.items():
			deckString += f"#{attr} = {val}\n"
		deckString += "-% BEGIN DECK %-\n"
		for section, cards in self._deck.items():
			deckString += f"[{section.title()}]\n"
			writeCards = {}
			for card in cards:
				try:
					writeCards[str(card.BasicCardID)] += 1
				except KeyError:
					writeCards[str(card.BasicCardID)] = 1
			for ID, count in writeCards.items():
				deckString += f"& {ID}"
				if count > 1:
					deckString += f" * {count}"
				deckString += "\n"
		deckString += r"-% END DECK %-"
		return deckString


	def __len__(self):
		"""
		Check the sum of all cards in self._deck
		"""
		rTotal = 0
		for section in self._deck.values():
			rTotal += len(section)

		return rTotal 

	def __iter__(self):
		for key, values in self._deck.items():
			yield key, values 

	def idDict(self):
		for section, cards in self._deck.items():
			yield section, [card.BasicCardID for card in cards]

	def json(self):
		return {
		"ATTRIBUTES" : {attr: val for attr, val in self.attributes.items()},
		 "DECK" : {section: cards for section, cards in self.idDict()}}

	def templateReady(self): #Django compatibility as templates does not allow access to _decks
		try:
			checkedIds = []
			self.deckDict = {}
			for section, cards in self:
				sectionName = re.sub(" ", "_", section)
				self.deckDict[sectionName] = []
				for card in cards:
					if card.BasicCardID in checkedIds:
						pass
					else:
						self.deckDict[sectionName].append(
							{card : self.checkCardCount(section, card.BasicCardID)})
						checkedIds.append(card.BasicCardID)
			return True
		except:
			return False

	def parseDeck(self, deckString=None):
		"""
		Parse a SBD file with either the filename given or a string passed to the function
		This will overwrite the previous deck and attributes
		"""
		if not deckString:
			with open(self.file, "r") as F:
				fileText = F.read()

		else:
			fileText = deckString

		self._deck = {}
		deckBegin = False	
		lineNumber = 1
		
		#Core parser	
		for line in fileText.split("\n"):
			if line.startswith("/") or not line.strip():
				#Empty lines are ignored aswell as lines that begin with a /
				pass

			elif deckBegin:
				#Only comments, sections and cards can be within the deck				
				newSection = re.search(r"(?<=\[)(.*)(?=\])", line)
				if line.startswith("&"):
					if not sectionName:
						raise ParseError(f"Card added to no section - line {lineNumber}: Please check your deck")
					ID = re.search(r"(?<=&)\s*[0-9]*(?=(|\s*\*))", line).group(0).strip(" ")
					if not cardIsInSection(sectionName, ID):
						#Ensure that the card ID is in the correct type area
						raise ParseError(
							f"ID: {ID} is not of type {sectionName} - line {lineNumber}: Please check your deck")
					count = re.search(r"(?<=\*)\s*[0-9]*(?=\s*(\n|/|$))", line)
					if count:
						#Count must be > 0 and <= 3 unless its swarm which has no card max
						count = int(count.group(0))
						if (not count <= 3 and not isSwarm(ID)) or count < 1:
							raise ParseError(f"Invalid card count - line {lineNumber}: Please check your deck")
					else:
						count = 1

					self._deck[sectionName] += [getBasicCard(ID)] * count

				elif re.search("(?i)-% END DECK %-", line):
					#-% END DECK %- Denotes the end of the deck all lines after this will thus be ignored
					print("END LINE FOUND")
					break

				elif newSection:
					#All cards must be assigned to one of five sections
					#Sections can be shown in the assertSection function
					sectionName = newSection.group(0).upper()
					assertSection(sectionName)
					self._deck[sectionName] = []

				else:
					raise ParseError(
						f"""Unknown line start within the deck build - line {lineNumber}:
						 {line} - Please check your deck""")

			elif re.search("(?i)-% BEGIN DECK %-", line):
				#Denotes the start of deck construction
				print("Deck construction start")
				deckBegin = True

			
			elif line.startswith("#"):
				#Denotes a tag to be assigned to the attributes dict
				if deckBegin:
					raise ParseError(
						f"Tag found within the deck - line {lineNumber}: Please check your deck")
				else:
					self.attributes[re.search("(?<=#)(.*)(?= =)", line).group(0).strip(" ").casefold()] \
				 = re.search(r"(?<== )(.*)(?=$)", line).group(0).split("/")[0].strip(" ")

			else:
				raise ParseError(
					f"""Unknown line start within the deck build - line {lineNumber}:
					 {line} - Please check your deck""")
			lineNumber += 1
		totalCards = len(self)
		if totalCards != 40:
			raise DeckError(f"Your deck has {totalCards}: 40 cards are required.")
		else:
			return self._deck

	def writeDeck(self, file=None):
		"""
		Writes the string of self to either given file or self.file
		"""		
		self.validateDeck()
		if file:
			f = file
		else:
			file = self.file
		with open(file, "w") as F:
			F.write(str(self))
		return True

	def dictToDeck(self, deck):
		"""
		Assign a deck dictionary to the class
		"""
		tmpDeck = {}
		for key, values in deck.items():
			assertSection(key)
			tmpDeck[key.upper()] = []
			for card in values:
				if type(card) != BasicCardInstance:
					tmpDeck[key.upper()].append(BasicCardInstance(card)) 
				else:
					tmpDeck[key.upper()].append(card)

		self._deck = tmpDeck
		return True

	def checkCardCount(self, section, ID):
		"""
		Check how many of card ID are in a given section
		"""
		assertSection(section)
		assert (cardIsInSection(section, ID))
		count = 0
		for card in self._deck[section.upper()]:
			if int(card.BasicCardID) == int(ID):
				count += 1

		if count > 3 and not isSwarm(ID):
			raise DeckError(f"This deck contains too many of one card - ID: {ID}")
		else:
			return count

	def validateDeck(self):
		"""
		Ensure the deck follows the rules:
		Exactly 40 cards
		All decks must contain at least 4 regular monsters
		No more thsn 3 of one card
		Swarm cards ignore the 3 of rule
		"""
		#All decks must have these tags
		if "owner" not in [a.casefold() for a in self.attributes.keys()]:
			self.attributes["owner"] = "No owner"
		if "date" not in [a.casefold() for a in self.attributes.keys()]:
			self.attributes["date"] = str(datetime.datetime.now())[:10]
		if "deckname" not in [a.casefold() for a in self.attributes.keys()]:
			self.attributes["DeckName"] = "No deck name"

		assert (len(self) == 40)
		for section, cards in self._deck.items():
			assertSection(section)
			if section.casefold() == "regular monsters":
				if len(cards) < 4:
					raise DeckError("Your deck contains less than 4 regular monsters")
			for card in cards:
				self.checkCardCount(section, card.BasicCardID)	

		return True	



	def addCards(self, Dict):
		"""
		Add a dict of IDs to the deck:
		e.g: {"REGULAR_MONSTERS" : [1, 1, 1, 2, 2, 3]}
		Will add cards until it breaks a rule
		"""
		for section, IDs in Dict.items():
			assertSection(section.upper())
			for ID in IDs:
				assert (len(self) < 40)
				assert (self.checkCardCount(section, ID) < 3 and not isSwarm(ID))
				self._deck[section.upper()].append(getBasicCard(ID))

		return True


	def removeCard(self, ID, count, section):
		"""
		Remove x amount of cards with given ID from a section
		"""
		section = section.upper()
		assertSection(section)
		for card in self._deck[section]:
			if int(card.BasicCardID) == int(ID):
				self._deck[section].remove(card)
				return True
		return False


def assertSection(sectionName):
	"""
	section names must be in -
	 TITAN MONSTERS,
	 REGULAR MONSTERS, 
	 MAGIC,
	 GEAR,
	 EVENT
	"""
	assert (sectionName.upper() in [
	 "TITAN MONSTERS",
	 "REGULAR MONSTERS", 
	 "MAGIC",
	 "GEAR",
	 "EVENT"
	])

def cardIsInSection(sectionName, ID):
	"""
	Ensure that the given ID for a card belongs to that section defined in the db
	"""
	assertSection(sectionName)
	if sectionName.casefold() in [
		"regular monsters",
		"titan monsters"
	]:
		sectionName = sectionName[:-1]
	conn = sqlite3.connect(DB_DIR)
	c = conn.cursor()
	cardType  = c.execute("""
		SELECT CardTypeName FROM tlkpCardType WHERE CardTypeID = 
		(SELECT CardTypeID FROM tblBasicCards WHERE BasicCardID = ?);
		""", (ID,)).fetchone()[0]
	if cardType.casefold() == sectionName.casefold():
		return True
	else:
		return False

try:
	from api.templatetags.apiFunctions import isSwarm

except ImportError:	

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

