"""Replace the opponent-occluded native idle capture with complete game pixels."""
from pathlib import Path
import json, shutil, sys, subprocess
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image
root=Path('assets/jubei-animality')
backup=root/'versions/before-complete-native-idle';backup.mkdir(parents=True,exist_ok=True)
for f in root.iterdir():
 if f.is_file() and not (backup/f.name).exists():shutil.copy2(f,backup/f.name)
if not (backup/'gd').exists():shutil.copytree(root/'gd',backup/'gd')
native=Path('assets/native-roster');saved=backup/'native-roster';saved.mkdir(exist_ok=True)
for name in ('jubei.png','jubei-reference.png','roster.json'):
 if not (saved/name).exists():shutil.copy2(native/name,saved/name)
im=Image.open('reports/native-jubei-fixed-roster-45.png').convert('RGBA');bg=im.getpixel((0,0))[:3]
im.putdata([(0,0,0,0) if p[:3]==bg else p for p in im.get_flattened_data()])
b=im.getbbox();im=im.crop(b)
ax,ay,compression=map(int,Path('reports/native-jubei-fixed-anchor.txt').read_text().split())
assert compression==0,compression
roster=json.loads((native/'roster.json').read_text());r=next(r for r in roster if r['slug']=='jubei')
old=Image.open(saved/'jubei.png').convert('RGBA')
assert im.height==old.height
anchor=[ax-b[0],ay-b[1]]
# Compare actor-relative pixels, independently of crop dimensions.
old_at={(x-r['anchor'][0],y-r['anchor'][1]):old.getpixel((x,y)) for y in range(old.height) for x in range(old.width) if old.getpixel((x,y))[3]}
new_at={(x-anchor[0],y-anchor[1]):im.getpixel((x,y)) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))[3]}
assert all(new_at.get(p)==v for p,v in old_at.items()),'Existing native pixels changed'
added=len(new_at)-len(old_at);assert added>50,added
im.save(native/'jubei.png');im.resize((im.width*6,im.height*6),Image.Resampling.NEAREST).save(native/'jubei-reference.png')
r.update(reference_size=list(im.size),anchor=anchor,compression=compression)
(native/'roster.json').write_text(json.dumps(roster,indent=2))
subprocess.run([sys.executable,'reports/build-roster-animality.py','jubei'],check=True)
for i in range(1,15):
 assert (root/f'frame-{i:02d}.png').read_bytes()==(backup/f'frame-{i:02d}.png').read_bytes(),i
out=Image.new('RGBA',(256,128),(35,42,56,255))
for col,folder in enumerate((backup,root)):out.alpha_composite(Image.open(folder/'frame-00.png').convert('RGBA'),(col*128,0))
out.resize((1024,512),Image.Resampling.NEAREST).save('reports/jubei-native-fixed-comparison.png')
message=f'PASS complete native Jubei: {added} restored pixels; every prior pixel preserved; animal/morph frames 01..14 unchanged.'
Path('reports/jubei-native-fixed-verification.txt').write_text(message+'\n')
print(message)
