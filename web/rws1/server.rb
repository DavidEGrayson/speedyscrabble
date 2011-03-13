require 'em-websocket'

module Clients
  def by_name(name)
    puts self.inspect
  end
end

$clients = {}
$clients.extend(Clients)

class Client
  attr_accessor :ws
  def initialize(websocket)
    @ws = websocket
    @name = assign_name(@ws.request["Query"]["name"])
  end

  def sanitize_user_name(raw_name)
    puts raw_name
    name = raw_name.to_s.scan(/[[:alnum:]]/).join[0,25]
    name.empty? ? "Guest" : name
  end

  def assign_name(requested_name)
    requested_name = sanitize_user_name(requested_name)
    existing_names = $clients.collect{|c| c.name}    
    while(existing_names.include?(name))
    
    end
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
    if Handlers.respond_to?(msg[0])
      Handlers.send(msg[0], ws, msg[1..-1])
    end
  }
  ws.onclose {
    $clients.delete(ws)
    puts "WebSocket closed"
  }
end
