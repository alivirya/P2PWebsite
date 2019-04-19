// The two functions below show an overlay when creating an event

function creating() {
	document.getElementById("overlaysidebar").style.display = "block";
}


function off() {
    document.getElementById("overlaysidebar").style.display = "none";
}

//when the page reloads, run the function get Session User
$(function() {
	getSessionUser()
});


//retrieve information about the event from cherrypy and udpate the details in html
function updateEvents(session) {
	var target = new XMLHttpRequest();
	target.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
			Events =  JSON.parse(this.response);
			EventInfo = '';
			AttendingDecision='';
			Attending = ''
			for (var key in Events) {
				var startTime = new Date(0);
				startTime.setUTCSeconds(Events[key]['start_time']);
				var endTime = new Date(0);
				endTime.setUTCSeconds(Events[key]['end_time']);
				if (Events[key]['sender'] != session) {
					Image = UrlExists(Events[key]['event_picture'])
					Host =  '<span class="tooltiptext" style="position: absolute;z-index: 1;top: -5px;left: 105%;" ><b>Host  :   </b>' + Events[key]['sender'] + '</br>'; 
					Event =  '<div class = "tooltip" ><b>Event   :   </b>' + Events[key]['event_name'] + ' ';
					Description =  '<b>Description   :   </b>' + Events[key]['event_description'] + '</br>';
					Location =  '<b>Location   :   </b>' + Events[key]['event_location'] + '</br>';
					Picture =  '<img src ="'+ Image+ '" style ="height: 80px; width: auto">';
					StartTime =  '<b>Start Time  :   </b>' + startTime+ '</br>'; 
					EndTime =  '<b>End Time  :   </b>' + endTime + '</br>';
					AttendingDecision =`</br><form action="/respondToEvent" style="display: inline-block"> 
  						<select name="attendance"> 
    						<option value="0" selected>Not Going</option> 
    						<option value="2">Maybe</option> 
    						<option value="1">Going</option>
    						<input  style="display: none" name = "event_name" value ="`+ Events[key]['event_name']+`" readonly>
    						<input  style="display: none" name = "start_time" value ="`+ Events[key]['start_time']+`" readonly>
      						<input  style="display: none" name = "host" value ="`+ Events[key]['sender']+`" readonly>

  						</select>  <input type="submit"></form>     `
  					if (Events[key]['attendee'] != null) {	
  						if (Events[key]['attendance'] == 0) {
  							attendance = 'Not Going'
  						}	
  						else if (Events[key]['attendance'] == 1) {
  							attendance = 'Going'
  						}	
  						else if (Events[key]['attendance'] == 2) {
  							attendance = 'Maybe'
  						} 
  						else if (Events[key]['attendance'] >= 3) {
  							attendance = 'Could not respond! '
  						}
  						Attending = '<b>' + Events[key]['attendee'] + '</b>  :  ' + attendance + '</span></div></br>';
   					}
   					else {
   						Attending = '</span></div></br>'
   					}

				}
				if (Events[key]['sender'] == session) {
					Attending = ''
					Image = UrlExists(Events[key]['event_picture'])
					Host =  '<span class="tooltiptext" style="position: absolute;z-index: 1;top: -5px;left: 105%;" ><b>Guests  :   </b>' + Events[key]['destination'] + '</br>'; 
					Event =  '<div class = "tooltip" ><b>Hosting Event   :   </b>' + Events[key]['event_name'] + '!';
					Description =  '<b>Description   :   </b>' + Events[key]['event_description'] + '</br>';
					Location =  '<b>Location   :   </b>' + Events[key]['event_location'] + '</br>';
					Picture =  '<img src ="'+ Image + '" style ="height: 80px; width: auto">';
					StartTime =  '<b>Start Time  :   </b>' + startTime+ '</br>'; 
					EndTime =  '<b>End Time  :   </b>' + endTime + '</br>';
  					if (Events[key]['attendee'] != null) {	
  						if (Events[key]['attendance'] == 0) {
  							attendance = 'Not Going'
  						}	
  						else if (Events[key]['attendance'] == 1) {
  							attendance = 'Going'
  						}	
  						else if (Events[key]['attendance'] == 2) {
  							attendance = 'Maybe'
  						} 
  						Attending = '<b>' + Events[key]['attendee'] + '</b>  :  ' + attendance+ '</span></div></br>';
   					}
   					else {
   						Attending = '</span></div></br>'
   					}
   					AttendingDecision =''
				}
  					EventInfo += Picture + '</br>' + Event + Host + Description + Location + StartTime + EndTime +Attending + AttendingDecision+ '</br>';
					
			}
			document.getElementById("event").innerHTML = EventInfo;
		}
	}


target.open("GET", "/returnEvents", true);
target.send();
};


//this function gets the current session user and updates the event accordingly
function getSessionUser() {
	var target = new XMLHttpRequest();
	target.onreadystatechange = function() {
    	if (this.readyState == 4 && this.status == 200) {
    		session = this.response
    		document.getElementById("profile").innerHTML = '<a href="/profile?user='+session+'">Profile</a>'
    		updateEvents(session)

    	}
    }
target.open("GET", "/returnSessionUser", true);
target.send();
};

//checks if the url provided for the image exists, if not, replace with a calender image
function UrlExists(url) {
    var http = new XMLHttpRequest();
    http.open('HEAD', url, false);
    http.send();
    if (http.status != 404)
       return url
    else
        return 'static/images/cal.png'
}
