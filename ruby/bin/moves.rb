# Usage: moves.rb WORD1 WORD2...

require_relative '../lib/speedyscrabble'

dictionary = Dictionary.new
dictionary.moves(ARGV).each do |m|
  puts m.inspect
end
