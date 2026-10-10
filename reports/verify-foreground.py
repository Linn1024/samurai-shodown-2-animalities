"""Compare Lua clipping against raw native C-ROM transparency and hardware zoom."""
from pathlib import Path
import struct,re,sys
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image
root=Path('reports')
v=struct.unpack('<65536H',(root/'foreground-vram.bin').read_bytes())
layers=struct.unpack('>381H',(root/'foreground-layers.bin').read_bytes())
chunks=[]
for c in range(1,9,2):
 a=next(Path('work/hack').glob(f'063-c{c}*')).read_bytes();b=next(Path('work/hack').glob(f'063-c{c+1}*')).read_bytes()
 raw=bytearray(len(a)*2);raw[0::2]=a;raw[1::2]=b;chunks.append(raw)
gfx=b''.join(chunks);zoomy=Path('assets/foreground/zoom-y.bin').read_bytes()
source=Path('tools/HBMAME/docs/release/src/hbmame/video/neogeo_spr.cpp').read_text()
table=source.split('static const int zoom_x_tables[][16] =',1)[1].split('};',1)[0]
xt=[[int(n) for n in re.findall(r'\d+',row)] for row in re.findall(r'\{([^{}]+)\}',table)]
def mask(override=None):
 result=set();x=y=zx=zy=rows=0
 for bank in range(381):
  ctrl=v[0x8200+bank];z=v[0x8000+bank] if override is None else (override//16)*256+override
  if ctrl&64:x=(x+zx+1)&511
  else:x=v[0x8400+bank]>>7;y=(512-(ctrl>>7))&511;rows=ctrl&63;zy=z&255
  zx=z>>8&15
  if not rows or not 0x100<=layers[bank]<65535:continue
  for sy in range(224):
   line=(sy+16-y)&511
   if rows<32 and line>=rows*16:continue
   zl=line&255;invert=bool(line&256)
   if invert:zl^=255
   if rows>32:
    zl%=2*(zy+1)
    if zl>zy:zl=2*(zy+1)-1-zl;invert=not invert
   lookup=zoomy[zy*256+zl];ty=lookup&15;row=lookup>>4
   if invert:ty^=15;row^=31
   t,attr=v[bank*64+row*2:bank*64+row*2+2];t|=(attr&240)<<12
   if t*128+128>len(gfx):continue
   if attr&2:ty^=15
   dx=0
   for sourcex,keep in enumerate(xt[zx]):
    if not keep:continue
    px=((x+dx)&511);dx+=1
    if px>=320:continue
    tx=sourcex^15 if attr&1 else sourcex
    offset=t*128+ty*4+(64 if tx<8 else 0)
    if any(gfx[offset+k]&(1<<(tx&7)) for k in range(4)):result.add(sy*320+px)
 return result
checks=[]
for zoom in (255,191,127):
 data=(root/f'foreground-mask-{zoom}.gd').read_bytes();expected=mask(zoom)
 actual={i for i,a in enumerate(data[11::4]) if a==127}
 assert actual==expected,(zoom,len(actual^expected))
 assert data[12::4]==bytes([17])*71680 and data[13::4]==bytes([34])*71680 and data[14::4]==bytes([51])*71680
 checks.append(f'PASS zoom {zoom}: {len(actual)} exact native opaque pixels; RGB preserved.')
native=(root/'foreground-native.gd').read_bytes();shown=(root/'foreground-best.gd').read_bytes();expected=mask()
assert expected and all(native[11+i*4:15+i*4]==shown[11+i*4:15+i*4] for i in expected),'Native barrel pixels must survive unchanged'
changed=sum(native[11+i*4:15+i*4]!=shown[11+i*4:15+i*4] for i in range(71680))
assert changed>100,'Animal must remain visible around the barrel'
checks.append(f'PASS actual FBNeo capture: {len(expected)} barrel pixels preserved; animal visible in {changed} other pixels.')
rgba=bytearray()
for a,r,g,b in zip(shown[11::4],shown[12::4],shown[13::4],shown[14::4]):rgba.extend((r,g,b,255-round(a*255/127)))
Image.frombytes('RGBA',(320,224),bytes(rgba)).resize((960,672),Image.Resampling.NEAREST).save('assets/haohmaru-animality/foreground-preview.png')
(root/'foreground-verification.txt').write_text('\n'.join(checks)+'\n')
print('\n'.join(checks))
