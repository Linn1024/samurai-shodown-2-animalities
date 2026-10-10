"""Independent raw-ROM raster comparison for 17 stages and three camera positions."""
from pathlib import Path
import struct,re,json,sys
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image,ImageDraw
chunks=[]
for c in range(1,9,2):
 a=next(Path('work/hack').glob(f'063-c{c}*')).read_bytes();b=next(Path('work/hack').glob(f'063-c{c+1}*')).read_bytes()
 raw=bytearray(len(a)*2);raw[0::2]=a;raw[1::2]=b;chunks.append(raw)
gfx=b''.join(chunks);zoomy=Path('assets/foreground/zoom-y.bin').read_bytes()
src=Path('tools/HBMAME/docs/release/src/hbmame/video/neogeo_spr.cpp').read_text()
table=src.split('static const int zoom_x_tables[][16] =',1)[1].split('};',1)[0]
xt=[[int(n) for n in re.findall(r'\d+',row)] for row in re.findall(r'\{([^{}]+)\}',table)]
roster=json.loads(Path('assets/native-roster/roster.json').read_text())
atlas=Image.new('RGB',(1280,5*248),(24,24,28));draw=ImageDraw.Draw(atlas)
checks=[];total=0
for index,character in enumerate(roster):
 slug=character['slug'];counts=[]
 for camera in range(1,4):
  root=Path(f'reports/stages/{slug}-{camera}')
  d=Path(str(root)+'-vram.bin').read_bytes();v=struct.unpack('<'+str(len(d)//2)+'H',d)
  layers=struct.unpack('>381H',Path(str(root)+'-layers.bin').read_bytes())
  expected=set();x=y=zx=zy=rows=0
  for bank in range(381):
   ctrl=v[0x8200+bank];z=v[0x8000+bank]
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
    tile,attr=v[bank*64+row*2:bank*64+row*2+2];tile|=(attr&240)<<12
    assert not attr&12,'Captured stage requires an animation counter fixture'
    if attr&2:ty^=15
    dx=0
    for sourcex,keep in enumerate(xt[zx]):
     if not keep:continue
     px=(x+dx)&511;dx+=1
     if px>=320:continue
     tx=sourcex^15 if attr&1 else sourcex
     offset=tile*128+ty*4+(64 if tx<8 else 0)
     if offset+3>=len(gfx):continue
     if any(gfx[offset+k]&(1<<(tx&7)) for k in range(4)):expected.add(sy*320+px)
  data=Path(str(root)+'-mask.gd').read_bytes()
  actual={i for i,a in enumerate(data[11::4]) if a==127}
  assert actual==expected,(slug,camera,len(actual^expected))
  assert data[12::4]==bytes([17])*71680 and data[13::4]==bytes([34])*71680 and data[14::4]==bytes([51])*71680
  counts.append(len(actual));total+=1
  if camera==1:
   native=Image.open(str(root)+'.png').convert('RGB')
   matte=Image.new('RGBA',(320,224))
   for pixel in actual:matte.putpixel((pixel%320,pixel//320),(255,40,200,150))
   native=native.convert('RGBA');native.alpha_composite(matte)
   x0=(index%4)*320;y0=(index//4)*248
   atlas.paste(native.convert('RGB'),(x0,y0+20));draw.text((x0+5,y0+4),slug+' | '+str(counts[0])+' foreground pixels',fill='white')
 checks.append(f'PASS {slug}: left/center/right, exact native foreground pixels {counts}.')
checks.append(f'PASS {total} scenes across all 17 native backgrounds; every alpha pixel and RGB byte checked.')
Path('reports/all-stage-foreground-verification.txt').write_text('\n'.join(checks)+'\n')
atlas.save('assets/foreground/stage-coverage.png')
print('\n'.join(checks))
