#!/usr/bin/ruby

def prompt(prompt)
  print prompt
  return gets.to_s.chomp
end

require 'speedyscrabble'

puts "Loading dictionary..."
dictionary = Dictionary.new

table = []
quit = false
table = Table.new(dictionary)

while !quit do
  command = prompt("> ").upcase
  if (command=="/QUIT")
    quit = true
    puts "Good game."
  else
    puts table.command(command)
  end
end
