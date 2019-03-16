import binascii


def fourCharsToInt(s):
    return int(binascii.hexlify(bytearray(s, 'ascii')), 16)

def intToFourChars(i):
    return binascii.unhexlify(format(i, 'x')).decode('ascii')
