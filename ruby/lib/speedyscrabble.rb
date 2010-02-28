#!/usr/bin/ruby

# This program lets you play Speedy Scrabble.
# http://www.davidegrayson.com/speedyscrabble/
#
# Author::    David Grayson (mailto:davidegrayson@gmail.com)
# License::   Creative Commons Attribution-Share Alike 3.0
#  http://creativecommons.org/licenses/by-sa/3.0/

# It is useful to add a function to the string class for this application.
class String
  # lsort rearranges all the characters in a string so that they
  # are in (alphabetical) order
  def lsort
    split("").sort.join("")
  end
end

class Array
  # yields each subset of self
  def each_subset(&block)
    i=0;
    limit = 2**size
    while (i < limit)
      subset = []
      each_index { |index| subset << at(index) if (i & (2**index) > 0);}
      yield(subset)
      i += 1
    end
  end

  # yields each subset of self that has size (self.size - num).
  # num can be an Integer, Array of Integers, or Range
  def each_missing(num, &block)
    if (num.is_a? Range) then
      num.each { |n| each_missing(n, &block) }
      return
    end

    if (num.is_a? Array) then
      num.each { |n| each_missing(n, &block) }
      return
    end

    if (!num.is_a?Integer) then
      raise "each_missing: num argument must be an Integer, Array of Integers, or Range.  num=#{num.inspect} which is a #{num.class}"
    end

    if (num==0) then
      yield self
      return
    end

    if (num > self.size) then
      return
    end

    each_index do |index|
      before_first_missing = self[0,index]
      #after_first_missing = self[index+1,size]
      self[index+1,size].each_missing(num-1) do |subset|
        yield before_first_missing+subset
      end
    end
  end
  
end

# The Dictionary class represents a dictionary; a list of words.  The dictionary is indexed by word.lsort in order to make it fast to look up anagrams.
class Dictionary
  attr_reader :data
  attr_reader :max_word_size

  # filename should be the name of a text file where each word in the dictionary is on
  # a separate line.
  def initialize(filename="data/dictionary.txt")
    file = File.new(filename, "r")
    @data = {}
    while (word = file.gets)
      if (word)
        word = word.chomp.upcase
        add_word(word)
      end
    end
    # @max_word_size = 4
  end

  # Adds a word to the dictionary.
  def add_word(word)
    sorted_word = word.lsort
    @data[sorted_word] ||= []
    @data[sorted_word] << word
    if (@max_word_size==nil) || (word.size > @max_word_size)
      @max_word_size = word.size
    end
  end

  # Computes the moves that are possible from an array of words/letters.
  # Returns an array; each element of the array is a move, represented by an
  # array of length two, move[0] is the word to make, and move[1] is the words/letters
  # that you can make it out of. 
  def moves(words)
    # words is an array of words/letters on the board e.g. ["RATE","ENCOUNTERED","T"]
    # Returns all possible moves
    words = words.collect{|word|word.upcase}

    moves = _moves([],words)

    # Apply the no-substring rule
    moves.delete_if do |move|
      reject = false
      move[1].each do |from_word|
        if ((from_word.size > 1) && (move[0].index(from_word) != nil)) then
          reject = true
        end
      end
      reject
    end

    return moves
  end

  protected
  # Returns all the moves that meet the following conditions:
  # Array yes_words: words that are definitely to be included in the move
  # Array maybe_words: words that might be included in the move
  def _moves(yes_words, maybe_words)

    # Avoid variable scope problems
    maybe_words = maybe_words.dup

    # COMPUTE yes_words_sum
    yes_words_sum = ""; yes_words.each{|word| yes_words_sum += word}

    # how close are we to reaching the size limit?
    free_size = self.max_word_size - yes_words_sum.size

    # delete the maybe_words that won't fit inside that space.
    # THIS IS THE HEART OF MAX_WORD_SIZE OPTIMIZATION!
    maybe_words.delete_if { |word| word.size > free_size }

    # Base case: no maybe_words
    if (maybe_words.size == 0) then
      if yes_words.size > 1 then
        #puts "Considering #{yes_words.inspect}"
        valid_moves = @data[yes_words_sum.lsort]
        if (valid_moves) then
          return valid_moves.collect{|word| [word,yes_words]}
        end
      end
      return []      
    end

    # Recursive case: call two copies of _moves

    moves = []

    first_maybe_word = maybe_words.shift  # changes maybe_words!

    # Case 1: Find moves that don't contain the first maybe word
    moves += _moves(yes_words, maybe_words)

    # Case 2: Find moves that contain the first maybe words
    moves += _moves(yes_words+[first_maybe_word], maybe_words)

    return moves
  end
  public


  # Formats an array of moves, like this:
  # 0) T+H+U+G -> THUG
  # 1) T+A+I+G -> GAIT
  # 2) T+A+H+G -> GHAT
  # 3) T+A+H+U -> HAUT
  # 4) T+A+H+U+G -> AUGHT
  # 5) T+A+H+U+G -> GHAUT
  def format_moves(moves)
    output = ""
    if moves.empty?
      output += "None."
    else
      moves.each_index do |index|
        output += "#{index}) " + format_move(moves[index]) + "\n"
      end
    end
    return output
  end

  # Formats a move, like this:
  # T+H+U+G -> THUG.
  # A move must be an array like this: ["THUG", ["T","H","U","G"]
  def format_move(move)
    to_word = move[0]
    from_words = move[1].join("+")
    return "#{from_words} -> #{to_word}"  
  end
end

# Represents a bag of scrabble tiles.
class Bag
  attr_accessor :letters # an array of letters

  # letters can be a string or array of all the letters in the bag.
  # If letters is left as nil, then the standard American scrabble
  # letter distribution is used. 
  def initialize(letters=nil)
    if letters==nil then
      letters = 'E'*12+'A'*9+'I'*9+'O'*8+'N'*6+'R'*6+'T'*6+'L'*4+'S'*4+'U'*4+'D'*4+'G'*3+'B'*2+'C'*2+'M'*2+'P'*2+'F'*2+'H'*2+'V'*2+'W'*2+'Y'*2+'K'*1+'J'*1+'X'*1+'Q'*1+'Z'*1
    end

    # shuffle the letters and store them as an array in @letters
    letters = letters.split("") if letters.is_a?(String)
    @letters = (1..(letters.size)).to_a.reverse.collect{|i|letters.delete_at(rand(i))}
  end

  # Draws a letter from the bag and returns it.  Returns nil if the bag is empty.
  # (Drawing a letter means it gets removed from the bag.)
  def draw
    letters.delete_at(rand(letters.size))
  end
end

# Represents a table where people could play speedy scrabble.
# Has words (an array of strings, which can also include single letters),
# a bag (see Bag class),
# and a dictionary (see Dictionary class)
class Table
  attr_accessor :dictionary
  attr_accessor :words
  attr_accessor :bag

  # You can specify your own dictionary, or just use the default one.
  def initialize(dictionary=Dictionary.new)
    @dictionary = dictionary
    @words = []
    @bag = Bag.new   
  end

  # formats the words on the table like this:
  # @words = ["FIRE", "MAN", "A"]
  def format_words
    return "@words = #{@words.inspect}"
  end

  # Runs a command.  These are the valid commands:
  # LETTER: add a letter to the board (equivalent to +LETTER)
  # +WORDS : add words to table, where WORDS is a space-separated list of words
  # -WORDS : remove words from table, where WORDS is a space-separated list of words
  # ? or /moves : print all the possible moves
  # # or /num : print the number of possible moves
  # NUMBER : make the move that was listed as NUMBER in the '?' command (see above).
  def command(command)
    output = ""

    # LETTER: equivalent to +LETTER
    if (command.match("^([A-Z])$")) then
      command = "+#{$1}"
    end

    # +WORD : add words to table
    if (command.match("^\\+([A-Z ]+)$"))
      new_words = $1.split(" ").delete_if{|word|word.empty?}
      @words += new_words
      output += "Added #{new_words.inspect} to table.\n"
      output += format_words

    # -WORD : remove words from table
    elsif (command.match("^-([A-Z ]+)$"))
      remove_words = $1.split(" ").delete_if{|word|word.empty?}
      words_copy = @words.dup
      valid = true
      remove_words.each do |word|
        index = words_copy.index(word)
        if index then
          words_copy.delete_at(index)
        else
          output += "Invalid removal: Not enough #{word.inspect}s on the table.\n"
          valid = false
        end
      end
      if valid then
        @words = words_copy
        output += "Removed #{remove_words.inspect} from table.\n"
      end
      output += format_words

    elsif (["@","/WORDS"].include?(command))
      output += format_words

    # # : number of moves
    elsif (["#","/num"].include?(command))
      output += "Number of possible moves: #{moves.size}"

    # ? : what moves can we make
    elsif (["?","/moves"].include?(command))
      output += "Possible moves:\n"+@dictionary.format_moves(moves)

    # number : make that move
    elsif (command.match("^([0-9]+)$"))
      move = moves[$1.to_i]
      if (move) then
        result = move(move)
        if result==true then
          output += "Made move: #{dictionary.format_move(move)}\n"+format_words
        else
          output += result
        end
      else
        output += "Unrecognized move #{$1.inspect}.  Enter '?' for a list of valid moves."  
      end

    else
      output += "Unrecognized command #{command.inspect}"
    end

    return output
  end

  ###### COMMANDS ########################

  # Makes a move, where move is an array like this:
  #  ["THUG", ["T","H","U","G"]]
  def move(move)
    to_word = move[0]
    from_words = move[1]

    # remove each of the "from words" from the board exactly once
    words_copy = @words.dup
    from_words.each do |word|
      index = words_copy.index(word)
      if index then
        words_copy.delete_at(index)
      else
        return "Invalid move #{dictionary.format_move(move)} : Not enough #{word.inspect}s on the table."
      end
    end
    @words = words_copy

    # add the "to word" to the board
    @words << to_word

    return true
  end

  # Draws a letter from the bag and adds it to the table and returns it.
  def draw
    letter = @bag.draw
    if letter then
      @words += [letter]
    end
    return letter
  end

  ###### COMPUTATATIONS / INFORMATION ##############

  # Returns an array of all the moves that are possible
  # with the current words.
  def moves
    if (@moves and @words_moves_were_computed_for==@words) then
      return @moves
    else
      @moves = dictionary.moves(@words)
      @words_moves_were_computed_for=@words
      return @moves
    end
  end

end





