#!/usr/bin/ruby
require 'speedyscrabble'

#require 'profiler'
require 'ruby-prof'

puts "Loading dictionary..."
dictionary = Dictionary.new
table = Table.new(dictionary)

puts "Profiling..."
RubyProf.start
#Profiler__::start_profile

# stress test:
moves = ["JUPE", "YOWL", "CION", "WOAD", "THIO", "LUNE", "EARN", "FERN", "GIED", "ATMA", "ERST", "FOSS", "DIVE", "IXIA", "YETI", "AGIO", "EPEE", "ORRA", "V", "DUCI", "BULK", "Q", "AZON", "R", "BELT", "MAST"]

puts dictionary.format_moves(dictionary.moves(moves))

#Profiler__::stop_profile
#Profiler__::print_profile($stderr)
result = RubyProf.stop
printer=RubyProf::GraphHtmlPrinter.new(result)
#printer = RubyProf::FlatPrinter.new(result)
printer.print(STDOUT, 0)
