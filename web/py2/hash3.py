#!/usr/bin/python3

import hashlib
import re
import struct

def get_key_value_1(key_str):
    number_string = ""
    space_count = 0
    for char in key_str:
        if char.isdigit():
            number_string += char
        if char == " ":
            space_count += 1
    return int(int(number_string)/space_count)

def get_key_value_2(key_str):
    key_number = int(re.sub("\\D", "", key_str))
    spaces = re.subn(" ", "", key_str)[1]
    if key_number % spaces != 0:
        raise BaseException("not integral")
    return key_number / spaces

def process_key(key_str):
    uint32 = get_key_value_1(key_str)
    print("Key value computed way 1: " + str(uint32))
    floaty = get_key_value_2(key_str)
    print("Key value computed way 2: " + str(uint32))
    return struct.pack("!I", uint32)

    #return bytes([uint32 & 0xFF, uint32>>8 & 0xFF, uint32>>16 & 0xFF, uint32>>24 & 0xFF])

key1 = "Uv3   \C5] 82  t00!2 64 d"
key2 = "q rh4 1 %1 5  D k2I7 7[89  0"
eight_bytes = "12345678".encode("utf-8")

byte_string = process_key(key1) + process_key(key2) + eight_bytes

m = hashlib.md5()
m.update(byte_string)
md5sum = m.digest()

stri = ""
for b in md5sum:
     stri += str(b) + " "
print("computed md5sum: " + stri)
