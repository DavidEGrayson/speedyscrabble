
var ws;
var connected;
var userName;

// Called when the document has been loaded.
function start()
{
		if (!("WebSocket" in window))
		{
				status("You have no web sockets.");
				return;
		}
		
		status(false, "Trying to connect.");

		var name = getUrlParameter('name');
		
		//ws = new WebSocket("ws://258.graysonfamily.org:83/play?name=" + escape(name));
		//ws = new WebSocket("ws://192.168.1.110:83/play"); // cool server
		//ws = new WebSocket("ws://192.168.1.110:82/play"); // pywebsocket
		ws = new WebSocket("ws://192.168.1.110:83/play?name=" + escape(name));
		ws.onopen = onOpen;
		ws.onmessage = onMessage;
		ws.onclose = onClose;
}

function onClose()
{
		status(false, "Connection closed.");
}

function onOpen()
{
		// Web Socket is connected. You can send data by send() method.
	  status(true, "Connected.");
}

function onMessage(evt)
{
		if (evt.data == "")
		{
				// Received a keepalive message from the host.
				return;
		}

		// The first character is the command.  The rest is
    // the data.
	  var command = evt.data[0]
		var data = evt.data.slice(1)

		if (command=='c')
		{
				// Received a message for the chat room.
				chatView.add("<div class=\"chat_message\">"+sanitize(data)+"</div>");
		}
		else if (command=='e')
		{
				// Received a notification that a new user has arrived.
				chatView.add("<div class=\"chat_message\">" + data + " has entered.</div>");
				userList.add(data);
		}
		else if (command=='l')
		{
				// Received a notification that a user has left.
				chatView.add("<div class=\"chat_message\">" + data + " has left.</div>");
				userList.remove(data);
		}
		else if (command == 's')
		{
				// Received the current state of the chat room.
				// Currently all this has is a list of the particpants.
				var names = data.split(',')
				for (var i=0; i < names.length; i++)
				{
						userList.add(names[i])
				}
		}
		else if (command == 'n')
		{
				// Received the name that has been assigned to us by the server.
        userName = data;
		}
}

function status(new_connected, str)
{
		if (new_connected != connected)
		{
				connected = new_connected;
		    serverStatus = document.getElementById("server_status");
		    serverStatus.innerHTML = connected ? "Connected" : "Not connected.";
				document.body.className = connected ? "connected" : "not_connected";
    }
		chatView.add("<div class=\"status_message\">"+str+"</div>");
}

userList = {};
userList.docObj = document.getElementById("chat_user_list");
userList.add = function(name)
{
    // Assumption: name is alphanumeric, with no spaces
		// TODO: add it in the correct place so that the list is alphabetic
    userList.docObj.innerHTML += "<div id=\"user_list_item_" + name + "\">" + name + "</div>";

}

userList.remove = function(name)
{
		var uli = document.getElementById('user_list_item_'+name);
    if (uli)
		{
				userList.docObj.removeChild(uli);
		}
}
		
var chatView = document.getElementById("chatView");
chatView.add = function(str)
{
		this.innerHTML += str;
		this.scrollTop = this.scrollHeight+30;
}

function sendChat()
{
		var chat_input = document.getElementById('chat_input');
		var val = chat_input.value;
		if (val!='')
		{
				ws.send('c'+val);
				chat_input.value = '';
		}
}

function getUrlParameter(name)
{
		var regexS = "[\\?&]"+name+"=([^&#]*)";
		var regex = new RegExp(regexS);
		var results = regex.exec(window.location.href);
		return results == null ? "" : results[1];
}

function sanitize(str)
{
		return str.replace(/</g,"&lt;").replace(/>/g,"&gt;");
}
