function getVals() {
	//Function to get only selected vals you don't have a stupid long url in your browser
	this.sForm = document.getElementById("SearchForm");
	this.getRequest = "?";
	this.getNext = false;

	this.checkVals = function(ele) {
		if (this.getNext && ele.type != "checkbox") {
			this.getRequest += "&" + ele.name + "=" + ele.value;

		} else {}
		if (ele.type == "checkbox") {
			if (ele.checked) {
				this.getNext = true;
				return;
			} else {
				this.getNext = false;
				return;
			}
		}
	}

	this.submitSearch = function() {
		for (var i=0; i<this.sForm.elements.length; i++) {
			if (this.sForm[i].type == "reset") {  break; }
			this.checkVals(this.sForm[i]);
		}
		return this.getRequest;
	}
}

function handleCheckbox(checkBox, slider) {
	if (!checkBox.checked) {
		slider.setAttribute('disabled', true);
	} else {
		slider.removeAttribute('disabled');
	}
}

function changePage(page) {
	newUrl = window.location.href.replace(/page=?(.*)/, "page=" + page);
	if (newUrl == window.location.href) {
		window.location.href = window.location.href + "&page=" + page

	} else {
		window.location.href = newUrl;
	}

}
