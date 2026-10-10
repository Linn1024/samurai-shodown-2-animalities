"""Tag Nicotine's straw hat with native hat slots, independently of feather/skin colors.
Run after rebuilding the owl frames. Polygons are in the unscaled 128px canvas.
The binary stores one native palette index per pixel; 255 means normal mapping.
"""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image,ImageDraw,ImageFilter
root=Path('assets/nicotine-animality')
polygons=[
 [(34,59),(42,44),(60,35),(73,32),(94,39),(80,46),(54,54)],
 [(37,55),(44,40),(60,30),(73,27),(99,35),(81,43),(57,50)],
 [(34,62),(44,47),(58,40),(70,35),(88,38),(101,44),(83,51),(58,58)],
 [(26,66),(32,54),(48,45),(63,41),(78,44),(96,50),(83,56),(58,62)],
 [(28,74),(39,68),(55,63),(70,62),(84,66),(100,76),(84,79),(59,79)],
 [(56,71),(55,63),(65,55),(75,52),(86,55),(102,65),(87,70),(69,73)],
 [(31,68),(43,56),(55,49),(68,47),(83,53),(99,61),(80,65),(55,67)],
 [(45,84),(55,78),(66,73),(76,72),(89,76),(103,84),(90,89),(70,90)],
 [(52,85),(59,73),(68,67),(79,67),(91,72),(103,76),(86,82),(67,85)],
 [(24,80),(28,67),(40,56),(54,49),(66,47),(83,52),(71,60),(48,69)],
 [(56,76),(52,68),(58,62),(69,60),(81,62),(98,74),(83,78),(66,78)],
 [(57,74),(58,59),(63,54),(72,56),(84,63),(96,74),(80,77)],
]
polygons += [polygons[3],polygons[2],polygons[1],polygons[0]]
mapping=json.loads((root/'palette-map.json').read_text())
colors={tuple(c[:3]):c[3] for c in mapping['colors']}
hat={i:next(tuple(c[:3]) for c in mapping['colors'] if c[3]==i) for i in (11,12,13,14,15)}
data=bytearray();preview=Image.new('RGBA',(512,512),(35,42,53,255));counts=[]
for frame,polygon in enumerate(polygons):
 im=Image.open(root/f'frame-{frame:02d}.png').convert('RGBA')
 mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon(polygon,fill=255)
 # Include the one-pixel straw edge around the hand-traced interior.
 mask=mask.filter(ImageFilter.MaxFilter(7))
 tagged=bytearray([255]*(128*128));review=im.copy();n=0
 for y in range(128):
  for x in range(128):
   r,g,b,a=im.getpixel((x,y))
   if not a or not mask.getpixel((x,y)):continue
   # Only the straw's warm shades/dark edges, never blue clothing or pale face/breast.
   if not ((r>=g>=b and r-g<100 and g>b*1.2) or r==g==b==0):continue
   index=min(hat,key=lambda i:sum((v-w)**2 for v,w in zip((r,g,b),hat[i])))
   tagged[y*128+x]=index;n+=1
   review.putpixel((x,y),(*hat[index],255))
 data.extend(tagged);counts.append(n);preview.alpha_composite(review,(frame%4*128,frame//4*128))
(root/'hat-palette.bin').write_bytes(data)
preview.resize((1024,1024),Image.Resampling.NEAREST).save('reports/owl-hat-palette-preview.png')
assert all(n>80 for n in counts),counts
print('Hat pixels per frame:',counts)
