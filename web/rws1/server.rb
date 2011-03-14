require 'em-websocket'

module Clients
  def by_name(name)
    puts self.inspect
  end
end

$clients = {}
$clients.extend(Clients)

class Client
  #attr_accessor :chatroom
  attr_accessor :ws
  def initialize(websocket)
    @ws = websocket
    @name = assign_name(@ws.request["Query"]["name"])
  end

  def sanitize_user_name(raw_name)
    name = raw_name.to_s.scan(/[[:alnum:]]/).join[0,25]
    name.empty? ? "Guest" : name
  end

  def assign_name(requested_name)
    name = sanitize_user_name(requested_name)
    existing_names = $clients.collect{|ws, c| c.name}    
    if existing_names.include?(name)
      i = 2
      while existing_names.include?(name + i.to_s)
        i += 1
      end
      name += i.to_s
    end
    return name
  end

  def name
    @name
  end
end

module Handlers
  def self.c(ws, msg)
    $clients.each do |ws2, c|
      ws2.send "c#{$clients[ws].name}: #{msg}"
    end
  end
end

EventMachine::WebSocket.start(:host=>"", :port=>8080) do |ws|
  ws.onopen {
    $clients[ws] = Client.new(ws)
    ws.send "n#{$clients[ws].name}"
  }
  ws.onmessage { |msg|
    command, data = msg[0], msg[1..-1]
    if Handlers.respond_to?(command)
      Handlers.send(command, ws, data)
    end
  }
  ws.onclose {
    $clients.delete(ws)
    puts "WebSocket closed"
  }
end
