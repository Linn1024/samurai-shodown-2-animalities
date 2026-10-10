from pathlib import Path
import struct
d=Path('reports/shadow-vram-2600.bin').read_bytes()
v=struct.unpack(f'<{len(d)//2}H',d)
for bank in range(0x51,0x5a):
    print(hex(bank),'zoom,y,x',[hex(v[a+bank]) for a in [0x8000,0x8200,0x8400]],'tiles',[hex(x) for x in v[bank*64:bank*64+4]])
for filename,start in [('063sp5.p1',0),('063sp.p2',0x100000)]:
    rom=bytearray(Path('work/hack',filename).read_bytes())
    rom[0::2],rom[1::2]=rom[1::2],rom[0::2]
    if start==0:
        for ident in [0x151c,0x3dc7]:
            entry=struct.unpack_from('>I',rom,0x72000+ident*4)[0]
            address=(entry&0xffff0007)*2+0x82004
            print('FRAME',hex(ident),hex(entry),hex(address))
    for pattern in [bytes.fromhex('6e40'),bytes.fromhex('6e42')]:
        hits=[]; p=0
        while (p:=rom.find(pattern,p))>=0:
            hits.append(hex(start+p)); p+=2
        print(filename,pattern.hex(),hits[:60])
