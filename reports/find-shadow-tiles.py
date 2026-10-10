from pathlib import Path
import struct
hits={}
for name,base in [('063sp5.p1',0),('063sp.p2',0x100000)]:
    d=bytearray(Path('work/hack',name).read_bytes());d[0::2],d[1::2]=d[1::2],d[0::2]
    for p in range(0,len(d)-4,2):
        tile,attr=struct.unpack_from('>HH',d,p)
        if 0x6e00<=tile<=0x6eff and 0x2210<=attr<=0x2213:
            hits.setdefault(tile,[]).append(base+p)
for tile,addresses in sorted(hits.items()):
    print(hex(tile|0x10000),'count',len(addresses),'first',','.join(hex(a) for a in addresses[:6]))
