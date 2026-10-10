"""Import imagegen morph drawings and a fresh Sieger sheet without drawing pixels.

Sources/prompts live in transformation-generation-v2.json. Build candidates first;
install with --install after inspecting transformation-review-v2.png.
"""
from pathlib import Path
import argparse,json,shutil,subprocess,sys
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image,ImageDraw
parser=argparse.ArgumentParser();parser.add_argument('--install',action='store_true');args=parser.parse_args()
roster=json.loads(Path('assets/native-roster/roster.json').read_text())
generation=json.loads(Path('reports/transformation-generation-v2.json').read_text())
stages=Path('reports/distinct-transformation-candidates');stages.mkdir(exist_ok=True)

def pieces(im,minimum=20):
 im=im.convert('RGBA');im.putdata([(r,g,b,255) if a>=160 else (0,0,0,0) for r,g,b,a in im.get_flattened_data()])
 pix=im.load();seen=set();groups=[]
 for y in range(im.height):
  for x in range(im.width):
   if (x,y) in seen or not pix[x,y][3]:continue
   todo=[(x,y)];seen.add((x,y));points=[]
   while todo:
    px,py=todo.pop();points.append((px,py))
    for dx,dy in ((-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)):
     nx,ny=px+dx,py+dy
     if 0<=nx<im.width and 0<=ny<im.height and (nx,ny) not in seen and pix[nx,ny][3]:
      seen.add((nx,ny));todo.append((nx,ny))
   if len(points)>=minimum:
    xs,ys=zip(*points);groups.append(((min(xs),min(ys),max(xs)+1,max(ys)+1),points))
 return im,groups

def stage_for(slug):
 root=Path('assets')/(slug+'-animality');stage=stages/slug;stage.mkdir(exist_ok=True)
 if not args.install:
  for f in root.iterdir():
   if f.is_file():shutil.copy2(f,stage/f.name)
 return root,stage

for slug,g in generation.items():
 root,stage=stage_for(slug)
 if args.install:
  backup=root/'versions/before-distinct-transformations-v2';backup.mkdir(parents=True,exist_ok=True)
  for f in root.iterdir():
   if f.is_file() and not (backup/f.name).exists():shutil.copy2(f,backup/f.name)
  if not (backup/'gd').exists():shutil.copytree(root/'gd',backup/'gd')
  for f in stage.iterdir():
   if f.is_file():shutil.copy2(f,root/f.name)
  shutil.copytree(stage/'gd',root/'gd',dirs_exist_ok=True)
  if slug=='sieger':
   ref=root/'versions/fresh-rhino-v2-size-reference';ref.mkdir(exist_ok=True)
   for f in stage.iterdir():
    if f.is_file():shutil.copy2(f,ref/f.name)
  print('Installed',slug,flush=True);continue
 meta=next(r for r in roster if r['slug']==slug)
 cfg=json.loads((root/'build-config.json').read_text())
 cfg['canvas_size']=json.loads((root/'asset-manifest.json').read_text())['cell'][0]
 source=Path(g['path'])
 if not source.exists():source=root/('source-v2.generated.png' if slug=='sieger' else 'transform-v2.generated.png')
 shutil.copy2(source,stage/('source-v2.generated.png' if slug=='sieger' else 'transform-v2.generated.png'))
 (stage/'prompt-transform-v2.txt').write_text(g['prompt'],encoding='utf-8')
 if slug=='sieger':
  raw=Image.open(source).convert('RGBA');assert abs(raw.width-1448)<=2 and abs(raw.height-1086)<=2,raw.size
  raw=raw.resize((raw.width//2,raw.height//2),Image.Resampling.NEAREST);raw.save(stage/'source-v2.png')
  _,groups=pieces(raw,1000);assert len(groups)==12,len(groups)
  boxes=[b for b,p in groups];assert all(b[0]>0 and b[1]>0 and b[2]<raw.width and b[3]<raw.height for b in boxes)
  scale=min(1,(meta['reference_size'][1]-1)/max(b[3]-b[1] for b in boxes),170/max(b[2]-b[0] for b in boxes))
  cfg.update(source_file='source-v2.png',source_scale=1,native_size_source=True,source_size=list(raw.size),animal_scale=round(scale,6),repeat_stand=True,size_reference='versions/fresh-rhino-v2-size-reference')
  cfg.pop('transformation_overrides',None)
  (stage/'prompt-v2-spacing.txt').write_text(g['spacing_prompt'],encoding='utf-8')
 else:
  sheet=Image.open(source).convert('RGBA');pair=[]
  for col in range(2):
   cell,groups=pieces(sheet.crop((col*sheet.width//2,0,(col+1)*sheet.width//2,sheet.height)))
   assert groups,(slug,col,'no sprite')
   largest=max(len(p) for _,p in groups);groups=[(b,p) for b,p in groups if len(p)>=max(20,largest*.003)]
   cleaned=Image.new('RGBA',cell.size);dest=cleaned.load();pix=cell.load()
   for b,points in groups:
    for x,y in points:dest[x,y]=pix[x,y]
   box=cleaned.getbbox();assert box[0]>0 and box[1]>0 and box[2]<cell.width and box[3]<cell.height,(slug,'source clipped',box)
   pair.append(cleaned.crop(box))
  old=[Image.open(root/f'frame-{i:02d}.png').convert('RGBA') for i in (0,3)]
  boxes=[im.getbbox() for im in old]
  target_h=round(meta['reference_size'][1]*.92)
  target_w=round(max(b[2]-b[0] for b in boxes)*1.12)
  scale=min(1,target_h/max(im.height for im in pair),target_w/max(im.width for im in pair))
  native=Image.open(Path('assets/native-roster')/(slug+'.png')).convert('RGBA')
  colors=list(dict.fromkeys(p[:3] for p in native.get_flattened_data() if p[3]))+[(232,248,248),(208,232,240),(168,200,224),(112,144,184),(64,80,128)]
  pal=Image.new('P',(1,1));pal.putpalette(sum((list(c) for c in colors),[])+[0]*(768-len(colors)*3))
  manifest=json.loads((root/'asset-manifest.json').read_text());size=manifest['cell'][0];anchor=manifest['anchor'];files=[]
  for i,im in enumerate(pair,1):
   im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
   alpha=im.getchannel('A');im=im.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');im.putalpha(alpha)
   canvas=Image.new('RGBA',(size,size));pos=(anchor[0]-round(im.width*.55),anchor[1]-im.height)
   assert pos[0]>0 and pos[1]>0 and pos[0]+im.width<size and pos[1]+im.height<size,(slug,'canvas clipped')
   canvas.alpha_composite(im,pos);file=f'transform-v2-{i:02d}.png';canvas.save(stage/file);files.append(file)
  cfg['transformation_overrides']=files
 (stage/'build-config.json').write_text(json.dumps(cfg,indent=2)+'\n')
 subprocess.run([sys.executable,'reports/build-roster-animality.py',slug,'--asset-dir',str(stage)],check=True)
 for i in (0,15):assert (root/f'frame-{i:02d}.png').read_bytes()==(stage/f'frame-{i:02d}.png').read_bytes(),(slug,'native endpoint changed')
 if slug!='sieger':
  for i in range(3,13):assert (root/f'frame-{i:02d}.png').read_bytes()==(stage/f'frame-{i:02d}.png').read_bytes(),(slug,i,'attack changed')

if not args.install:
 out=Image.new('RGB',(800,len(roster)*160),(45,48,56));d=ImageDraw.Draw(out)
 for row,r in enumerate(roster):
  root=stages/r['slug'] if r['slug'] in generation else Path('assets')/(r['slug']+'-animality')
  d.text((4,row*160+3),r['slug'],fill='white')
  for col,i in enumerate(range(4)):
   im=Image.open(root/f'frame-{i:02d}.png').convert('RGBA');im=im.crop(im.getbbox())
   out.paste(im,(col*200+(200-im.width)//2,row*160+150-im.height),im)
   d.text((col*200+177,row*160+3),str(i),fill='white')
 out.save('reports/transformation-review-v2.png')
 for part,(start,end) in enumerate(((0,9),(9,17)),1):out.crop((0,start*160,800,end*160)).save(f'reports/transformation-review-v2-{part}.png')
