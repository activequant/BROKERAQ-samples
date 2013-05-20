#
# Filename
#
#   bincalc.py
#
# Author
#
#   Chris Hager <chris@metachris.org>
#
# Description
#
#   Utils for encoding the bit representations of numbers
#
#   - Varint: Base 128 variable length integers (using only lower 7 bits of the byte)
#   - ZigZag: Transforming negative numbers into positives (0=0, 1=2, 2=4, -1=1, -2=3, ...)
#   - numberToBytes: Minimal byte representation of a number, without leading empty bytes 
#
#   Big-Endian ordering is used everywhere (for all bits in bytes, and for all 
#   bytes in a byte-group (most significant comes first). 
#
#

def numberToZigZag(n):
    """
    ZigZag-Encodes a number:
       -1 = 1
       -2 = 3
        0 = 0
        1 = 2
        2 = 4
    """
    return (n << 1) ^ (n >> 31)

def zigZagToNumber(z):
    """ Reverses ZigZag encoding """
    return (z >> 1) if not z & 1 else -(z+1 >> 1)
    
def numberToBytes(n):
    """
    Returns the bytes representing the number, without most significant bytes if  
    empty. Starts at the rightmost (least significant) byte and traverse to the left. 
    """
    if n == 0:
        return bytearray([0x00])
        
    result = bytearray()
    while n > 0:
        result.insert(0, n & 255)
        n >>= 8        
    return result

def bytesToNumber(b):
    """
    Restoring the stripped bytes of an int or long into Python's built-in data types
    int or long.
    """   
    result = 0
    round = 0
    for byte in b:
        round += 1
        if round > 1:
            result <<= 8
        result |= byte
    return result
    
def numberToVarint(n):
    """ 
    Converts a number into a variable length byte array (using 7 bits per
    byte, big endian encoding, highest bit is info if last length-byte (0) or 
    not (1)). 
    
    Start at the lower byte (right) and work the way up :)    
    """
    value = int(n)
    if value == 0:
        return bytearray([0x00])
        
    result = bytearray()    
    round = 0
    while value > 0:
        # only use the lower 7 bits of this byte (big endian)
        # if subsequent length byte, set highest bit to 1, else just insert the value with 
        flag = 0
        if value>127:
            flag = 128 
        b = value & 127 | flag 
        result.append(b) # sets length-bit to 1 on all but first
        value >>= 7
        round += 1
    #ok, let's correct the byte order and the flags ... 
        
    
    return result

def varintToNumber(byteArray):
    """
    Converts a varlen bytearray back into a normal number, starting at the most 
    significant varint byte, adding it to the result, and pushing the result 
    7 bits to the left each subsequent round.
    """
    number = 0
    round = 0
    for byte in byteArray:
        round += 1
        if round > 1:
            number <<= 7
        number |= byte & 127 # only use the lower 7 bits
    return number        

def unicodeToByteArray(u):
    """ Simple conversion of unicode to bytearray: utf8 encoding """ 
    return bytearray(u.encode("utf-8"))
    
def byteArrayToUnicode(byteArray):
    """ Simple conversion of bytearray to unicode: utf8 decoding and casting """ 
    return unicode(byteArray.decode("utf-8"))
        
def printBits(byteArray):
    """
    Print all bits of a bytearray
    """
    print repr(byteArray)
    for byte in byteArray:
        c1 = "%3i | " % byte
        c2 = ""
        for _ in xrange(8):
            c2 = "%s%s" % ("1" if byte & 1 else "0", c2)
            byte >>= 1 
        print "%s%s" % (c1, c2)