f = File.open("word_frequency_raw.txt", "r")

exp = /\[\[([^',]+)\]\]\s*\|\|\s([0-9]+)/
while(!f.eof?)
  line = f.readline
  if (exp.match(line))
    puts $1 + "," + $2
  end
end
