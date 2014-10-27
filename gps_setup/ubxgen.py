#!/usr/bin/python
#
# ubx packet generator
#
# v0.2
#
# Wilfried Klaebe <wk-openmoko@chaos.in-kiel.de>
# NeilBrown <neilb@suse.de>
#
# Usage:
#
# ubxgen.py 06 13 04 00 01 00 00 00 > packet.ubx
#
# prepends 0xb5 0x62 header,
# appends checksum,
# outputs binary packet to stdout
#
# Numbers can be given in decimal with a suffix 'dN' where
# 'N' is the number of bytes.  These are converted in little-endian
# The value 'L' can be given which is th 2-byte length
# of the rest of the message
#
# you can send the packet to GPS chip like this:
#
# cat packet.ubx > /dev/ttySAC1

import sys
import binascii

cs0=0
cs1=0

sys.stdout.write("\xb5\x62")

outbuf = []
leng = None

for d in sys.argv[1:]:
    if d == 'L':
        leng = len(outbuf)
        outbuf.append(0)
        outbuf.append(0)
    elif 'd' in d:
        p = d.index('d')
        bytes = int(d[p+1:])
        d = int(d[0:p])
        while bytes > 0:
            b = d % 256
            d = int(d/256)
            outbuf.append(b)
            bytes -= 1
    else:
        c = binascii.unhexlify(d)
        outbuf.append(ord(c))

if leng != None:
    l = len(outbuf) - (leng + 2)
    outbuf[leng] = l % 256
    outbuf[leng+1] = int(l/256)

for c in outbuf:
    sys.stdout.write(chr(c))
    cs0 += c
    cs0 &= 255
    cs1 += cs0
    cs1 &= 255

sys.stdout.write(chr(cs0)+chr(cs1))
