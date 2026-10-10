"""Extract native sprite transparency for every stage and animation frame."""
from pathlib import Path
import sys,zipfile
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image
chunks=[]
for c in range(1,9,2):
 a=next(Path('work/hack').glob(f'063-c{c}*')).read_bytes()
 b=next(Path('work/hack').glob(f'063-c{c+1}*')).read_bytes()
 raw=bytearray(len(a)*2);raw[0::2]=a;raw[1::2]=b;chunks.append(raw)
gfx=b''.join(chunks)
root=Path('assets/foreground');root.mkdir(exist_ok=True)
# All native tiles: two bytes per row, sixteen rows per tile. Lazy lookup in Lua
# avoids a giant table and covers animated/broken props without hand-made lists.
opacity=bytearray()
for start in range(0,len(gfx),128):
 for y in range(16):
  a=start+y*4
  opacity.extend((gfx[a+64]|gfx[a+65]|gfx[a+66]|gfx[a+67],gfx[a]|gfx[a+1]|gfx[a+2]|gfx[a+3]))
(root/'sprite-opacity.bin').write_bytes(opacity)
# Native fixed-layer glyphs: two packed pixels per byte, low nibble first.
# FBNeo NeoTextDecodeTile groups raw bytes at 16/24/0/8 for each 8px row.
text=Path('work/hack/063-s1sp.s1').read_bytes();fixed=bytearray()
for start in range(0,len(text),32):
 for y in range(8):
  bits=0
  for group,offset in enumerate((16,24,0,8)):
   packed=text[start+offset+y]
   if packed&15:bits|=1<<(group*2)
   if packed>>4:bits|=1<<(group*2+1)
  fixed.append(bits)
(root/'fixed-opacity.bin').write_bytes(fixed)
# Intact foreground barrel: five rows, two columns, mirrored for its right half.
tiles=range(0x1e6a8,0x1e6b2)
lines=['-- Native C-ROM opacity: each tile has sixteen 16-bit row masks.','return {']
atlas=Image.new('RGBA',(16*len(tiles),16))
for column,tile in enumerate(tiles):
 data=gfx[tile*128:(tile+1)*128];rows=[]
 for y in range(16):
  row=0
  for x in range(16):
   offset=y*4+(64 if x<8 else 0)
   opaque=any(data[offset+k] & (1<<(x%8)) for k in range(4))
   if opaque:row|=1<<x;atlas.putpixel((column*16+x,y),(255,255,255,255))
  rows.append(row)
 lines.append(f' [0x{tile:x}]={{'+','.join(map(str,rows))+'},')
lines.append('}')
(root/'barrel-masks.lua').write_text('\n'.join(lines)+'\n')
atlas.resize((704,64),Image.Resampling.NEAREST).save(root/'barrel-opacity-tiles.png')
with zipfile.ZipFile('tools/FBNeo/roms/neogeo.zip') as z:
 name=next(n for n in z.namelist() if n.lower().endswith('000-lo.lo'))
 (root/'zoom-y.bin').write_bytes(z.read(name))
print(f'Built exact opacity for all {len(gfx)//128} native sprite tiles and native vertical zoom lookup.')
