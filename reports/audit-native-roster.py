"""Audit isolated native captures against opponent-free native recaptures."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image,ImageDraw
roster=json.loads(Path('assets/native-roster/roster.json').read_text())
stage=Path('reports/complete-native-candidates');stage.mkdir(exist_ok=True)
results=[];atlas=Image.new('RGB',(960,17*160),(35,42,56));d=ImageDraw.Draw(atlas)
def pixels(im,anchor):
 return {(x-anchor[0],y-anchor[1]):im.getpixel((x,y)) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))[3]}
for n,r in enumerate(roster):
 slug=r['slug'];src=Image.open(f'reports/native-{slug}-complete-roster-45.png').convert('RGBA');bg=src.getpixel((0,0))[:3]
 src.putdata([(0,0,0,0) if p[:3]==bg else p for p in src.get_flattened_data()])
 b=src.getbbox();src=src.crop(b)
 ax,ay,z=map(int,Path(f'reports/native-{slug}-complete-anchor.txt').read_text().split());anchor=[ax-b[0],ay-b[1]]
 assert z==0,(slug,z)
 src.save(stage/(slug+'.png'))
 old=Image.open(f'assets/native-roster/{slug}.png').convert('RGBA')
 a,c=pixels(old,r['anchor']),pixels(src,anchor)
 added=len(c.keys()-a.keys());removed=len(a.keys()-c.keys());changed=sum(v!=c[p] for p,v in a.items() if p in c)
 entry=dict(slug=slug,added=added,removed=removed,recolored=changed,size=list(src.size),anchor=anchor)
 results.append(entry);print(entry,flush=True)
 for col,im in enumerate((old,src)):
  canvas=Image.new('RGBA',(192,144));anc=r['anchor'] if col==0 else anchor
  canvas.alpha_composite(im,(90-anc[0],140-anc[1]))
  canvas=canvas.resize((384,288),Image.Resampling.NEAREST)
  # Native resolution at 1x in shared actor coordinates keeps long swords visible.
  canvas=canvas.resize((192,144),Image.Resampling.NEAREST)
  atlas.paste(canvas,(col*320,n*160+16),canvas)
 d.text((650,n*160+30),f"{slug}\nRestored: {added}\nRemoved: {removed}\nRecolored: {changed}",fill='white')
Path('reports/complete-native-audit.json').write_text(json.dumps(results,indent=2))
d.text((4,0),'OLD                                    COMPLETE GAME CAPTURE',fill='white')
atlas.save('reports/complete-native-audit.png')
