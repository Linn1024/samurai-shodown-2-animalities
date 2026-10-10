"""Pack an entirely fresh wolf using only new source and native human pixels.

No installed wolf images/configuration are opened. --install archives the old
files without examining their contents, then copies the reviewed candidate.
"""
from pathlib import Path
import argparse,json,shutil,subprocess,sys
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image,ImageDraw
parser=argparse.ArgumentParser();parser.add_argument('--install',action='store_true');args=parser.parse_args()
stage=Path('reports/galford-fresh-v6');stage.mkdir(exist_ok=True)
root=Path('assets/galford-animality')
if args.install:
 backup=root/'versions/before-fresh-v6';backup.mkdir(parents=True,exist_ok=True)
 for file in root.iterdir():
  if file.is_file() and not (backup/file.name).exists():shutil.copy2(file,backup/file.name)
 if not (backup/'gd').exists():shutil.copytree(root/'gd',backup/'gd')
 for file in stage.iterdir():
  if file.is_file():shutil.copy2(file,root/file.name)
 shutil.copytree(stage/'gd',root/'gd',dirs_exist_ok=True)
 reference=root/'versions/fresh-v6-size-reference';reference.mkdir(exist_ok=True)
 for file in stage.iterdir():
  if file.is_file():shutil.copy2(file,reference/file.name)
 print('Installed entirely new v6 wolf. Previous art archived without viewing.');sys.exit()
g=json.loads(Path('reports/galford-fresh-v6-generation.json').read_text())
source=Path(g['path'])
if not source.exists():source=stage/'source-v6.generated.png'
if source.resolve()!=(stage/'source-v6.generated.png').resolve():shutil.copy2(source,stage/'source-v6.generated.png')
(stage/'prompt-v6.txt').write_text(g['prompt'],encoding='utf-8')
if g.get('spacing_prompt'):(stage/'prompt-v6-spacing.txt').write_text(g['spacing_prompt'],encoding='utf-8')
raw=Image.open(source).convert('RGBA')
# Nearest-neighbor normalization only; artwork comes exclusively from imagegen.
raw=raw.resize((raw.width//2,raw.height//2),Image.Resampling.NEAREST);raw.save(stage/'source-v6.png')
raw.putdata([(r,g,b,255) if a>=160 else (0,0,0,0) for r,g,b,a in raw.get_flattened_data()])
pix=raw.load();seen=set();groups=[]
for y in range(raw.height):
 for x in range(raw.width):
  if (x,y) in seen or not pix[x,y][3]:continue
  todo=[(x,y)];seen.add((x,y));points=[]
  while todo:
   px,py=todo.pop();points.append((px,py))
   for dx,dy in ((-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)):
    nx,ny=px+dx,py+dy
    if 0<=nx<raw.width and 0<=ny<raw.height and (nx,ny) not in seen and pix[nx,ny][3]:
     seen.add((nx,ny));todo.append((nx,ny))
  if len(points)>=1000:
   xs,ys=zip(*points);groups.append((min(xs),min(ys),max(xs)+1,max(ys)+1))
assert len(groups)==12,('Expected twelve complete new drawings',len(groups))
assert all(b[0]>0 and b[1]>0 and b[2]<raw.width and b[3]<raw.height for b in groups),('Source cropped at boundary',groups)
# Latest requested size: 20% below Galford's 109px human height (~87px).
scale=min(1,87/max(b[3]-b[1] for b in groups),170/max(b[2]-b[0] for b in groups))
cfg=dict(source_file='source-v6.png',source_scale=1,native_size_source=True,source_size=list(raw.size),animal_scale=round(scale,6),canvas_size=192,movement='crouch_pounce',repeat_stand=True,size_reference='versions/fresh-v6-size-reference')
(stage/'build-config.json').write_text(json.dumps(cfg,indent=2)+'\n')
subprocess.run([sys.executable,'reports/build-roster-animality.py','galford','--asset-dir',str(stage)],check=True)
frames=[Image.open(stage/f'frame-{i:02d}.png').convert('RGBA') for i in range(16)]
assert len({im.tobytes() for im in frames[:4]})==4
assert frames[13].tobytes()==frames[2].tobytes() and frames[14].tobytes()==frames[1].tobytes()
assert frames[0].tobytes()==frames[15].tobytes() and frames[3].tobytes()==frames[12].tobytes()
native=Image.open('assets/native-roster/galford.png').convert('RGBA')
assert frames[0].crop(frames[0].getbbox()).tobytes()==native.crop(native.getbbox()).tobytes()
for i,im in enumerate(frames):
 b=im.getbbox();assert b[0]>0 and b[1]>0 and b[2]<192 and b[3]<192
 assert set(im.getchannel('A').get_flattened_data())<={0,255}
 if i not in (0,15):assert b[3]-b[1]<=87
out=Image.new('RGB',(800,640),(40,45,56));d=ImageDraw.Draw(out)
for i,im in enumerate(frames):
 col,row=i%4,i//4;im=im.crop(im.getbbox());out.paste(im,(col*200+(200-im.width)//2,row*160+150-im.height),im)
 d.text((col*200+5,row*160+5),str(i),fill='white')
out.save('reports/galford-fresh-v6-review.png')
print('PASS native humans, two distinct hybrids, reversed return, stable readiness, hard alpha, no clipping, 87px height cap.')
