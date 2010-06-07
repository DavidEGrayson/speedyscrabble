
var ws;

/* Called when the document has been loaded. */
function start()
{
    userList.docObj = document.getElementById("chat_user_list");

		if (!("WebSocket" in window))
		{
				status("You have no web sockets.");
				return;
		}
		
		status("Trying to connect.");

		var name = getUrlParameter('name');
		
		ws = new WebSocket("ws://258.graysonfamily.org:83/play?name=" + escape(name));
		
		ws.onopen = function() {
				// Web Socket is connected. You can send data by send() method.
				status("Connected.");
		};
		
		ws.onmessage = function (evt)
				{
						var command = evt.data[0]
						var data = evt.data.slice(1)
						if (command=='z')
						{
								// Received a server status message.
								var sd = document.getElementById("server_status");
								sd.innerHTML = data;
						}
						else if (command=='c')
						{
								// Received a message for the chat room.
								addChatElement("<div class=\"chat_message\">"+data+"</div>");
						}
						else if (command=='e')
						{
								// Received a notification that a new user has arrived.
								addChatElement("<div class=\"chat_message\">" + data + " has entered.</div>");
								userList.add(data);
						}
						else if (command=='l')
						{
								// Received a notification that a new user has arrived.
								addChatElement("<div class=\"chat_message\">" + data + " has left.</div>");
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
				};
		
		ws.onclose = function()
				{
						status("Connection closed.");
				};
}

function status(str)
{
		addChatElement("<div class=\"status_message\">"+str+"</div>");
}

userList = {};
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

function addChatElement(str)
{
		var cm = document.getElementById("chat_messages");
		cm.innerHTML += str;
		cm.scrollTop = cm.scrollHeight+30;
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
		//name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
		var regexS = "[\\?&]"+name+"=([^&#]*)";
		var regex = new RegExp(regexS);
		var results = regex.exec(window.location.href);
		return results == null ? "" : results[1];
}