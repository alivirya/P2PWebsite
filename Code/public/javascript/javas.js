setUpUsers()
session = ''
//set getting session users and updating users to occur every 15 seconds
window.setInterval(function(){
 	getSessionUser()
 	setUpUsers()
}, 15000);


//change the user depending on what the current page is    
function changeUsers(user) {
	var http = new XMLHttpRequest();
	var url = "/setActiveUser";
	var params = "user=" + user;
	http.open("POST", url, true);

	//Send the proper header information along with the request
	http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");

	http.onreadystatechange = function() {//Call a function when the state changes.
    	if(http.readyState == 4 && http.status == 200) {
  			
    	}
	}
http.send(params);
}

//set up the user bar. It also calls the function displayUser when any of the links are clicked
function setUpUsers() {
	var user = new XMLHttpRequest();
	user.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
    		Users = JSON.parse(this.responseText);
			var User = '';
			for (var key in Users) {
				var color;
				if (Users[key].online == 1) {
					text = 'online'
					color = '#488214';
				} else if (Users[key].online == 2) {
					text  = 'idle'
					color = '#FF8C00';
				} else if (Users[key].online == 3) {
					text = 'away'
					color = '#FFD700';
				} else if (Users[key].online == 4) {
					text = 'do not disturb'
					color = '#000';
				} else {
					text = 'offline'
					color = '#8B0000';
				}
				User += '<li><a href="javascript:displayUser(\''+key+'\',\''+ session + '\')">'+ key+'<div class = "tooltip" style="margin-top:5px;border-radius: 50px; width : 20px;height:20px;background:' + color + ';display:inline-block; float:right"><span class="tooltiptext">'+ text+'</span></div></br><p style="font-size: 15px;">Last Online: ' +Users[key].lastlogin+'</p></a></li>';
       		}
       		document.getElementById("userId").innerHTML = User;
    	}
    }
user.open("GET", "/returnUserList", true);
user.send();
};


//if the page reloads, reload setting up the users and display information about the session user
$(function() {
	getSessionUser()
	setUpUsers()
});



//this function displays information about the user clicked on
function displayUser(user, session) {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
    		window.history.pushState(user, 'Title', '/?upi='+user);
    		changeUsers(user);
			document.getElementById("send").value = user
    		Messages = JSON.parse(this.responseText);
			var Length = Object.keys(Messages).length;
			var Message = '';
			var Time = '';
			for (var key in Messages) {
				if (Messages[key].sender == user && Messages[key].destination == session) {
					if (Messages[key].filename != null) {
						if (Messages[key].content_type.indexOf('image') >= 0) {
							Message += '<img src="static/media/' + Messages[key].filename + '" class="msgPicture">';
						} else if (Messages[key].content_type.indexOf('audio') >= 0) {
							Message += '<audio controls style="margin: 0 auto;display: block;"> <source src="static/media/' + Messages[key].filename + '" type="' + Messages[key].content_type + '"">Your Browswer doesnt support audio</audio>'
						}
						else if (Messages[key].content_type.indexOf('video') >= 0) {
							Message += '<video style = "margin: 0 auto; display: block;" height="200" width="auto" controls> <source src="static/media/' + Messages[key].filename + '" type="' + Messages[key].content_type + '"">Your Browswer doesnt support Video</audio>'
						} else {
							Message += '<div class="msgLine"><a href="static/media/' + Messages[key].filename + '">'+ Messages[key].filename + '</a></div>'
						}

					}
					if (Messages[key].message != null) {
						Message += '<div class="msgLine">'+ Messages[key].sender+ '  :  ' + Messages[key].message + '<p class=time>' + Messages[key].stamp+'</p></div>';
					}
					else {
						Message +=  '<div class="msgLine">'+ Messages[key].sender+ '  :  '  + '<p class=time>' + Messages[key].stamp+'</p></div>';
					}
				}
				if (Messages[key].sender == session && Messages[key].destination == user) {
					if (Messages[key].filename != null) {
						if (Messages[key].content_type.indexOf('image') >= 0) {
							Message += '<img src="static/media/' + Messages[key].filename + '" class="msgPicture">';
						} else if (Messages[key].content_type.indexOf('audio') >= 0) {
							Message += '<audio controls style="margin: 0 auto;display: block;"> <source src="static/media/' + Messages[key].filename + '" type="' + Messages[key].content_type + '"">Your Browswer doesnt support audio</audio>'
						}
						else if (Messages[key].content_type.indexOf('video') >= 0) {
							Message += '<video style = "margin: 0 auto; display: block;" height="200" width="auto" controls> <source src="static/media/' + Messages[key].filename + '" type="' + Messages[key].content_type + '"">Your Browswer doesnt support Video</audio>'
						} else {
							Message += '<div class="msgLine"><a href="static/media/' + Messages[key].filename + '">'+ Messages[key].filename + '</a></div>'
						}

					}
					if (Messages[key].message != null) {
						Message += '<div class="msgLine" style="text-align: right;">'+ Messages[key].sender+ '  :  ' + Messages[key].message + '<p class=time style="float: left">' + Messages[key].stamp+'</p></div>';
					}
					else {
						Message +=  '<div class="msgLine" style="text-align: right;">'+ Messages[key].sender+ '  :  '  + '<p class=time style="float: left">' + Messages[key].stamp+'</p></div>';
					}
				}
			}
			document.getElementById("person").innerHTML = 'You are talking to ' + user + '!            Click <a href ="javascript:displayProfile( \''+ user+ '\')">here</a> to open their profile!'
			document.getElementById("msgs").innerHTML = Message;
    	}
    }
xhttp.open("GET", "/returnMessages", true);
xhttp.send();
};




//turn off overlay
function off() {
    document.getElementById("overlaysidebar").style.display = "none";
}

//display information about the user clicked
function displayInformation(session) {
	var target = new XMLHttpRequest();
	target.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
			displayUser(this.response,session)
    	}
    }
target.open("GET", "/returnActiveUser", true);
target.send();
};

//get the user who is currently on the server
function getSessionUser() {
	var target = new XMLHttpRequest();
	target.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
    		session = this.response
    		document.getElementById("profile").innerHTML = '<a href="/profile?user='+session+'">Profile</a>'
    		displayInformation(session);
    	}
    }
target.open("GET", "/returnSessionUser", true);
target.send();
};

//display profile through the overlay. This is enabled when the button is clicked
function displayProfile(user) {
	var target = new XMLHttpRequest();
	target.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
			Profile = JSON.parse(this.response);
			for (var key in Profile) {
				if (key == user) {
        			var picture = '<img src = "'+ Profile[key].picture+ '" class="dp">';
					var name = '<p id="name" class="name">' + Profile[key].fullname+ '</p>';
					var position = '<p id="position" class ="position">Position:' + Profile[key].position + '</br>Location:' +Profile[key].location +'</br>Description:' + Profile[key].description + '</p>';
					var allData = picture + name + position;
				}
			}
			document.getElementById("text").innerHTML = allData
			document.getElementById("overlaysidebar").style.display = "block";

    	}
    }
target.open("GET", "/returnProfile", true);
target.send();
};



