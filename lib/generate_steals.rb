#!/usr/bin/ruby
require 'speedyscrabble'

DEPTH = 4   # how many-letter steals to consider
# 4-letter steals happen sometimes in games
# 5-letter steals are exceedingly rare

dictionary = Dictionary.new

# sdata format: sdata[lsort.size][lsort] = words
# tdata form: tdata[lsort.size] = number
#sdata = {}
#tdata = {}
#(1..dictionary.max_word_size).to_a.each do |size|
#  sdata[size] = {}
#  tdata[size] = 0
#end
#puts "Doing hard stuff..."
#dictionary.data.each do |lsort, words|
#  sdata[lsort.size][lsort] = words
#  tdata[lsort.size] += words.size
#end
#puts "Size, Number"
#(1..dictionary.max_word_size).to_a.each do |size|
#  puts "#{size}=>#{tdata[size]},"
#end

# Size Distribution: Size=>Number of words
size_distribution = {4=>3903,
  5=>8636,
  6=>15232,
  7=>23109,
  8=>28419,
  9=>24792,
  10=>20194,
  11=>15407,
  12=>11273,
  13=>7781,
  14=>5100,
  15=>3178}

puts "Starting the hard work..."

# steals[lsort] = smaller_lsorts
steals = {}
count = 0
dictionary.data.each do |lsort, words|
  steals[lsort] = []
  lsort.split("").each_missing(1..DEPTH) do |lsort_subset_array|
    lsort_subset = lsort_subset_array.join
    if dictionary.data.has_key?(lsort_subset) and lsort_subset_array.size < lsort.size
      steals[lsort] << lsort_subset
    end
    steals[lsort].uniq!
  end

  count += 1
  if (count % 1000)==0
    puts "#{count} lsorts analyzed"
  end
end

puts "Writing to file..."
my_file = File.new("steals.txt", "a")
my_file.puts steals.inspect

puts "Done!"

