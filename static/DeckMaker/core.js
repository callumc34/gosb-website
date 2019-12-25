function checkCardCount() {
	var deckLists = document.getElementsByClassName("deckList");
	var count = 0;
	Array.prototype.forEach.call(deckLists, function(e) {
		Array.prototype.forEach.call(e.children, function(ce) {
			count += Number(ce.children[1].value);
		});
	});
	return count;
}

function addToDeck(id, section, isswarm) {
	var count = checkCardCount();
	if (count >= 40) {
		alert("You cannot add more than 40 cards to a deck");
		return;
	}
	var sectionName;
	switch (section) {
		case "1":
			sectionName = "Regular monsters";
			break;
		case "2":
			sectionName = "Titan monsters";
			break;
		case "3":
			sectionName = "Gear";
			break;
		case "4":
			sectionName = "Magic";
			break;
		case "5":
			sectionName = "Event";
			break;
	}
	var isSet = false;
	var list = document.getElementById(sectionName).children[1];
	var cardCounter;
	Array.prototype.forEach.call(list.children, function(c) {
		if (id == c.getAttribute("idvalue")) {
			isSet = true;
			cardCounter = c.children[1];
		}
	});
	if (!isSet) {
		let cardImage = getUrl = /(.*)(?=deck)/.exec(window.location.href)[0] + "cards/image?ID=" + id;
		let liElement = document.createElement("li");
		let imgElement = document.createElement("img");
		let countElement = document.createElement("input");
		liElement.setAttribute("idvalue", id)
		countElement.setAttribute("type", "number");
		countElement.setAttribute("value", 1);
		countElement.setAttribute("min", 0);
		if (isswarm) {
			countElement.setAttribute("max", 40);
		} else {
			countElement.setAttribute("max", 3);
		}
		countElement.setAttribute("onchange", "updateCard(this)")
		countElement.setAttribute("class", "cardCount");
		imgElement.setAttribute("src", cardImage);
		imgElement.setAttribute("class", "cardImage");
		liElement.appendChild(imgElement);
		liElement.appendChild(countElement);
		list.appendChild(liElement);
	} else {
		if (cardCounter.value >= 3){
			return;
		} else {
			cardCounter.value = Number(cardCounter.value) + 1;
			}
	}

	document.getElementById("CardCount").innerHTML = "Card count: " + Number(count + 1);
}

function updateCard(input) {
	if (input.value < 1) {
		input.parentNode.parentNode.removeChild(input.parentNode);
	}
	var count = checkCardCount();
	if (count > 40) {
		alert("You cannot add more than 40 cards to a deck");
		input.value = input.value - 1;
	}
	document.getElementById("CardCount").innerHTML = "Card count: " + Number(count);
}

function updateTable(cards) {
	var cardJson = JSON.parse(cards);
	var cardTable = document.getElementById("SelectionTable").getElementsByTagName('tbody')[0];
	clearCards();
	cardJson["Cards"].forEach( function(card) {
		let nRow = cardTable.insertRow();
		let idCell = nRow.insertCell(0);
		let nameCell = nRow.insertCell(1);
		let deckCell = nRow.insertCell(2);
		idCell.appendChild(document.createTextNode(card["BasicCardID"]));
		idCell.style = "font-size: 32px;"
		nameCell.appendChild(document.createTextNode(card["BasicCardName"]));
		let deckButton = document.createElement("input");
		deckButton.setAttribute("type", "button");
		deckButton.setAttribute("name", "deckAdd");
		deckButton.setAttribute("value", "Add");
		deckButton.setAttribute("idvalue", card["BasicCardID"]);
		deckButton.setAttribute("section", card["CardTypeID"]);
		deckButton.setAttribute("isswarm", (card["PermFXID"] == 67));
		deckButton.setAttribute("onclick", "addToDeck(this.getAttribute('idvalue'), this.getAttribute('section'))");
		deckCell.appendChild(deckButton);
	});
}

function clearCards(form=document.getElementById("SelectionTable")) { 
	form.tBodies[0].innerHTML = form.tBodies[0].rows[0].innerHTML;
}

function fetchCards(form=document.getElementById("SelectionForm")) {
	getUrl = /(.*)(?=deck)/.exec(window.location.href)[0] + "api/cardSearch/?";
	if (form == null) {
		getUrl += "idValueMin=0&idValueMax=50";
	} else {
		Array.prototype.forEach.call(form.children[0].children, function(e) {
			if ((e.tagName == "SELECT" ||
			 e.tagName == "INPUT") && (e.type != "button" && e.type != "reset") &&
			  (e.value != false && e.value != "--Ignore--")) {
				getUrl += "&" + e.id + "=" + e.value;
			} else {
				return;
			}
		});
	}

    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            updateTable(xmlHttp.responseText);
    }
    xmlHttp.open("GET", getUrl, true); // true for asynchronous 
    xmlHttp.send(null);
}

function submitDeck() {
	var count = checkCardCount();
	if (count != 40) {
		alert("You do not have 40 cards in your deck");
		return;
	}
	
	var getUrl = /(.*)(?=deck)/.exec(window.location.href)[0] + "api/decks/create/";
	var deckData = {};
	var deckLists = document.getElementsByClassName("deckList");
	Array.prototype.forEach.call(deckLists, function(e) {
		var section = e.parentElement.id
		deckData[section] = [];
		Array.prototype.forEach.call(e.children, function(ce) {
			let idv = Number(ce.getAttribute("idvalue"));
			let cardCount = Number(ce.children[1].value);
			for (i=0; i<cardCount; i++) {
				deckData[section].push(idv);
			}
		});
	});
	window.location.href = getUrl + "?deck=" + JSON.stringify(deckData)
	 + "&Owner=" + document.getElementById("OwnerInput").value
	 + "&DeckName=" + document.getElementById("DeckNameInput").value
	 + "&redirect=True";
	
}