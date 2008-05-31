#!/usr/bin/ruby

require 'speedyscrabble'

table = Table.new

def coolest_move(moves)
  moves.first
end

continue = true

while(continue) do
  while (table.moves.size > 0)
    move = coolest_move(table.moves)
    table.move(move)
    puts "Made move: #{table.dictionary.format_move(move)}\n"+table.format_words
  end

  # Continue this loop if I can draw another letter
  result = table.draw
  continue = (result != nil)
  #puts "Drew a #{result.inspect}"
end

puts "There are no moves or tiles left.  Good game!"

puts "Number of words: #{table.words.size}"

words_sum=""; table.words.each{|word|words_sum+=word}
puts "Number of letters: #{words_sum.size}"


