"""Import two imagegen morphs per approved character, aligned to native idle.

Never changes native humans or completed animal/attack drawings. Stage, inspect
idle-morph-v3-review.png, then --install. Only crop/reduce/quantize/pack pixels.
"""
from pathlib import Path
import argparse,json,shutil,subprocess,sys
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image,ImageDraw
parser=argparse.ArgumentParser();parser.add_argument('--install',action='store_true');parser.add_argument('--slugs',nargs='+');args=parser.parse_args()
generation=json.loads(Path('reports/idle-morph-v3-generation.json').read_text())
if args.slugs:generation={s:g for s,g in generation.items() if s in args.slugs}
stages=Path('reports/idle-morph-v3-candidates');stages.mkdir(exist_ok=True)
measurements={}

def silhouette(cell):
 cell=cell.convert('RGBA');cell.putdata([(r,g,b,255) if a>=160 else (0,0,0,0) for r,g,b,a in cell.get_flattened_data()])
 pix=cell.load();seen=set();groups=[]
 for y in range(cell.height):
  for x in range(cell.width):
   if (x,y) in seen or not pix[x,y][3]:continue
   todo=[(x,y)];seen.add((x,y));points=[]
   while todo:
    px,py=todo.pop();points.append((px,py))
    for dx,dy in ((-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)):
     nx,ny=px+dx,py+dy
     if 0<=nx<cell.width and 0<=ny<cell.height and (nx,ny) not in seen and pix[nx,ny][3]:
      seen.add((nx,ny));todo.append((nx,ny))
   if len(points)>=20:groups.append(points)
 assert groups,'No drawn sprite'
 largest=max(map(len,groups));out=Image.new('RGBA',cell.size);target=out.load()
 for points in groups:
  if len(points)<max(20,largest*.001):continue
  for x,y in points:target[x,y]=pix[x,y]
 box=out.getbbox();assert box[0]>0 and box[1]>0 and box[2]<cell.width and box[3]<cell.height,('Source clipped',box)
 return out.crop(box)

for slug,g in generation.items():
 root=Path('assets')/(slug+'-animality');stage=stages/slug;stage.mkdir(exist_ok=True)
 if args.install:
  backup=root/'versions/before-idle-morph-v3';backup.mkdir(parents=True,exist_ok=True)
  for f in root.iterdir():
   if f.is_file() and not (backup/f.name).exists():shutil.copy2(f,backup/f.name)
  if not (backup/'gd').exists():shutil.copytree(root/'gd',backup/'gd')
  for f in stage.iterdir():
   if f.is_file():shutil.copy2(f,root/f.name)
  shutil.copytree(stage/'gd',root/'gd',dirs_exist_ok=True)
  print('Installed idle-connected morphs:',slug,flush=True);continue
 for f in root.iterdir():
  if f.is_file():shutil.copy2(f,stage/f.name)
 source=Path(g['path'])
 if not source.exists():source=root/'idle-morph-v3.generated.png'
 shutil.copy2(source,stage/'idle-morph-v3.generated.png')
 (stage/'prompt-idle-morph-v3.txt').write_text(g['prompt'],encoding='utf-8')
 if g.get('correction_prompt'):(stage/'prompt-idle-morph-v3-correction.txt').write_text(g['correction_prompt'],encoding='utf-8')
 sheet=Image.open(source).convert('RGBA');pair=[silhouette(sheet.crop((c*sheet.width//2,0,(c+1)*sheet.width//2,sheet.height))) for c in range(2)]
 if g.get('first_path'):
  first_source=Path(g['first_path'])
  if not first_source.exists():first_source=root/'idle-morph-v3-initial.generated.png'
  shutil.copy2(first_source,stage/'idle-morph-v3-initial.generated.png')
  first=Image.open(first_source).convert('RGBA');pair[0]=silhouette(first.crop((0,0,first.width//2,first.height)))
 cfg=json.loads((root/'build-config.json').read_text());meta=json.loads((root/'asset-manifest.json').read_text())
 size=meta['cell'][0];anchor=meta['anchor'];cfg['canvas_size']=size
 original=[Image.open(root/f'frame-{i:02d}.png').convert('RGBA') for i in (0,3)]
 boxes=[im.getbbox() for im in original];heights=[b[3]-b[1] for b in boxes]
 fractions=[(anchor[0]-b[0])/(b[2]-b[0]) for b in boxes]
 # Early anatomy inherits native idle's height and actor-relative placement.
 # Late anatomy interpolates toward the full animal's height and placement.
 targets=[heights[0],round(heights[0]*.35+heights[1]*.65)]
 ratios=[fractions[0],fractions[0]*.35+fractions[1]*.65]
 # Retain the human foot baseline even if it differs from generic animal anchor.
 baselines=[boxes[0][3],round(boxes[0][3]*.35+boxes[1][3]*.65)]
 native=Image.open(Path('assets/native-roster')/(slug+'.png')).convert('RGBA')
 colors=list(dict.fromkeys(p[:3] for p in native.get_flattened_data() if p[3]))+[(232,248,248),(208,232,240),(168,200,224),(112,144,184),(64,80,128)]
 pal=Image.new('P',(1,1));pal.putpalette(sum((list(c) for c in colors),[])+[0]*(768-len(colors)*3))
 files=[];measurements[slug]=[]
 for index,(im,height,ratio,baseline) in enumerate(zip(pair,targets,ratios,baselines),1):
  scale=min(1,height/im.height)
  # Keep complete long swords/gauntlets inside the existing canvas.
  scale=min(scale,(anchor[0]-1)/(im.width*ratio),(size-anchor[0]-1)/(im.width*(1-ratio)))
  im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
  if index==1:assert im.height==heights[0],(slug,'early morph must retain native idle height')
  alpha=im.getchannel('A');im=im.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');im.putalpha(alpha)
  canvas=Image.new('RGBA',(size,size));pos=(anchor[0]-round(im.width*ratio),baseline-im.height)
  assert pos[0]>0 and pos[1]>0 and pos[0]+im.width<size and pos[1]+im.height<size,(slug,'canvas clipped',pos,im.size)
  canvas.alpha_composite(im,pos);file=f'idle-morph-v3-{index:02d}.png';canvas.save(stage/file);files.append(file)
  measurements[slug].append(dict(frame=index,height=im.height,width=im.width,position=list(pos),baseline=baseline,anchor_fraction=ratio))
 cfg['transformation_overrides']=files
 (stage/'build-config.json').write_text(json.dumps(cfg,indent=2)+'\n')
 subprocess.run([sys.executable,'reports/build-roster-animality.py',slug,'--asset-dir',str(stage)],check=True)
 for i in (0,*range(3,13),15):assert (root/f'frame-{i:02d}.png').read_bytes()==(stage/f'frame-{i:02d}.png').read_bytes(),(slug,i,'unchanged drawing changed')
 frames=[Image.open(stage/f'frame-{i:02d}.png').convert('RGBA') for i in range(16)]
 assert len({im.tobytes() for im in frames[:4]})==4,slug
 assert frames[13].tobytes()==frames[2].tobytes() and frames[14].tobytes()==frames[1].tobytes(),slug
 for i,im in enumerate(frames):
  b=im.getbbox();assert b[0]>0 and b[1]>0 and b[2]<size and b[3]<size,(slug,i,'clipped')
  assert set(im.getchannel('A').get_flattened_data())<={0,255}

if not args.install:
 Path('reports/idle-morph-v3-measurements.json').write_text(json.dumps(measurements,indent=2))
 out=Image.new('RGB',(960,len(generation)*210),(40,45,56));d=ImageDraw.Draw(out)
 for row,slug in enumerate(generation):
  stage=stages/slug;d.text((5,row*210+4),slug,fill='white')
  for col,i in enumerate(range(4)):
   im=Image.open(stage/f'frame-{i:02d}.png').convert('RGBA');size=im.width
   # Render shared canvases so differences in alignment remain visible.
   out.paste(im,(col*240+(240-size)//2,row*210+210-size),im)
   d.text((col*240+180,row*210+4),str(i),fill='white')
 out.save('reports/idle-morph-v3-review.png')
 print('PASS unchanged humans/animal/attacks, two distinct stages, reverse return and safe packing.')
