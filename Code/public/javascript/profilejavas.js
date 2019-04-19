//the following functions turns on and off the display
function editProfile() {
	document.getElementById("overlaysidebar").style.display = "block";
}


function off() {
    document.getElementById("overlaysidebar").style.display = "none";
}

//calling the getSessionUser function everytime the page reloads
$(function() {
	getSessionUser()
});

//update the profile of the user
function updatePersonalProfile(session) {
	var target = new XMLHttpRequest();
	target.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
			Profile =  JSON.parse(this.response);
			document.getElementById("profilepic").src = Profile[session]['picture']
		}
	}


target.open("GET", "/returnProfile", true);
target.send();
};


//get the current user in session
function getSessionUser() {
	var target = new XMLHttpRequest();
	target.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
    		session = this.response
			document.getElementById("send").value = session;
    		document.getElementById("profile").innerHTML = '<a href="/profile?user='+session+'">Profile</a>'
    		updatePersonalProfile(session)

    	}
    }
target.open("GET", "/returnSessionUser", true);
target.send();
};
