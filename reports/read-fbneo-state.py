from pathlib import Path
import struct
d=Path('tools/FBNeo/savestates/samsh2sp slot 01.fs').read_bytes()
p=d.index(struct.pack('<I',0xa55a0000))+8
blocks=[]
def hash_name(text):
    h=0xc0ffee
    for c in text.encode():h=((h^c)+(h<<26)+(h>>6))&0xffffffff
    return h
names={hash_name(n):n for n in ['68K RAM','Graphics RAM','Sprite RAM','Palette RAM','NVRAM','Memory card','NeoGraphicsRAM','NeoPaletteRAM']}
while p+12<len(d):
    tag,size,name=struct.unpack_from('<III',d,p)
    if tag!=0xa55a0001: break
    blocks.append((p+12,size,name,d[p+12:p+12+size]))
    p+=12+size
for offset,size,name,content in blocks:
    if size>=0x8000:
        print(hex(offset),hex(size),hex(name),names.get(name,''))
        Path(f'reports/fbneo-state-block-{name:08x}.bin').write_bytes(content)
        if size==0x10000:
            ram=bytearray(content);ram[0::2],ram[1::2]=ram[1::2],ram[0::2]
            pointer=int.from_bytes(ram[0xa46:0xa4a],'big')
            if 0x100000<=pointer<0x110000:
                print('GAME RAM',hex(pointer))
                Path('reports/fbneo-state-game-ram.bin').write_bytes(ram)
                obj=0x2000;visited=set()
                while 0x2000<=obj<0xfd00 and obj not in visited:
                    visited.add(obj)
                    code=int.from_bytes(ram[obj:obj+4],'big')
                    blink=ram[obj+0x22]
                    if blink or code in [0x44790,0x124d4]:
                        print('OBJECT',hex(obj+0x100000),'handler',hex(code),'blink',hex(blink),'flags',hex(ram[obj+0x88]),'anim',ram[obj+0x64:obj+0x68].hex())
                    if ram[obj+0x10:obj+0x12]==b'\xff\xff':break
                    obj=int.from_bytes(ram[obj+0xe:obj+0x10],'big')
