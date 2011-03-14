require 'em-websocket'

class ChatRoom
  attr_accessor :clients

  def initialize
    @clients = {}
  end

  def add_client(websocket)
    @clients[websocket] = client = Client.new(websocket)
    client.name = assign_name(websocket.request["Query"]["name"])
    websocket.send "n" + client.name
    send_all "e" + client.name
  end

  def remove_client(websocket)
    client = @clients[websocket]
    @clients.delete(websocket)
    send_all "l" + client.name
  end

  def sanitize_user_name(raw_name)
    name = raw_name.to_s.scan(/[[:alnum:]]/).join[0,25]
    name.empty? ? "Guest" : name
  end

  def assign_name(requested_name)
    name = sanitize_user_name(requested_name)
    existing_names = @clients.collect{|ws, c| c.name}    
    if existing_names.include?(name)
      i = 2
      while existing_names.include?(name + i.to_s)
        i += 1
      end
      name += i.to_s
    end
    return name
  end

  def send_all(message)
    puts "send_all: #{message}"
    @clients.each do |websocket, client|
      websocket.send message
    end
  end

  def handle_message(websocket, message)
    command, data = "command_#{message[0]}", message[1..-1]
    if respond_to?(command, true)
      send(command, websocket, data)
    end
  end

  private
  def command_c(websocket, chat_message)
    send_all "c#{@clients[websocket].name}: #{chat_message}"
  end

end

class Client
  attr_reader :ws
  attr_accessor :name

  def initialize(websocket)
    @ws = websocket
  end
end

chatroom = ChatRoom.new

EventMachine::WebSocket.start(:host=>"", :port=>8080) do |ws|
  ws.onopen {
    chatroom.add_client(ws)
  }
  ws.onmessage { |msg|
    chatroom.handle_message(ws, msg)
  }
  ws.onclose {
    chatroom.remove_client(ws)
  }
end
