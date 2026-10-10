from pathlib import Path
import struct
d=Path('reports/fbneo-state-block-978eb9e4.bin').read_bytes()
v=struct.unpack('<65536H',d)
size=0
for bank in range(0x17d):
    attr=v[0x8200+bank]
    if not attr&0x40:size=attr&0x3f
    tiles=[]
    for row in range(min(size,32)):
        tile,flags=v[bank*64+row*2:bank*64+row*2+2]
        if flags>>8==0x22:
            tiles.append(hex(tile|((flags&0x70)<<12)))
    if tiles:print('BANK',hex(bank),'Y',hex(attr),'X',hex(v[0x8400+bank]),'TILES',tiles)
