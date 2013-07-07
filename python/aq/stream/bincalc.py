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
#   - numberToBytes: Minimal byte representation of a number, without leading empty bytes 
#
#   Big-Endian ordering is used everywhere (for all bits in bytes, and for all 
#   bytes in a byte-group (most significant comes first). 
#
#
    
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