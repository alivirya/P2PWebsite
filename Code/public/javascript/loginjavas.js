
//when the page is reloaded call the session user
$(function() {
	getSessionUser()
});


//retrieve the secret from cherrypy and put it into a qr code
function secret(user) {
	var target = new XMLHttpRequest();
	target.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
    		document.getElementById("qr").src = 'https://chart.googleapis.com/chart?chs=200x200&chld=M|0&cht=qr&chl=otpauth://totp/' + user  + '%3Fsecret%3D' + this.response + '%26issuer%3Dauthentication';
    	}
    }
target.open("GET", "/returnSecret", true);
target.send();
};


//retrieve the current session member
function getSessionUser() {
	var target = new XMLHttpRequest();
	target.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
    		session = this.response
    		secret(session);
    	}
    }
target.open("GET", "/returnSessionUser", true);
target.send();
};
