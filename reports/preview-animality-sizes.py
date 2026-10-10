"""Show all existing animals beside unscaled native human captures."""
from pathlib import Path
import sys,json,struct
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image,ImageDraw
roster=json.loads(Path('reports/animality-size-review.json').read_text())
out=Image.new('RGB',(1260,240*((len(roster)+2)//3)),(72,80,88));draw=ImageDraw.Draw(out)
for i,r in enumerate(roster):
 x=i%3*420;y=i//3*240;root=Path('assets')/(r['slug']+'-animality')
 for name,offset in [('frame-00.png',10),('frame-03.png',210)]:
  im=Image.open(root/name).convert('RGBA');im=im.crop(im.getbbox())
  out.paste(im,(x+offset,y+200-im.height),im)
 draw.line((x+5,y+201,x+410,y+201),fill=(110,118,126))
 draw.text((x+10,y+210),r['slug']+'  strike '+str(r['before']['strike'])+' -> '+str(r['after']['strike']),fill='white')
out.save('reports/animality-size-overview.png')
print('Saved reports/animality-size-overview.png at consistent native zoom.')
