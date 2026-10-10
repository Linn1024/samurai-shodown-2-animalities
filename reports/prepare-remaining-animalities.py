from pathlib import Path
import sys,json,shutil,subprocess
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image
base=Path('C:/Users/linn1/.codex/generated_images/01a12259-5416-7c60-8115-a389a45534d0')
files={'hanzo':'exec-caa1a387-3661-45e1-9297-015db401705c.png',
 'sieger':'exec-dc2ec4df-45a1-4439-945f-658f02f7ae08.png',
 'mizuki':'exec-dff5dd6a-182a-4e0f-9b19-5b7ed18b45cb.png'}
roster=json.loads(Path('assets/native-roster/roster.json').read_text())
for slug,file in files.items():
 root=Path('assets')/(slug+'-animality');root.mkdir(exist_ok=True)
 im=Image.open(base/file).convert('RGBA');assert im.size==(1448,1086),im.size
 shutil.copy2(base/file,root/'source-v1.generated.png')
 im=im.resize((724,543),Image.Resampling.NEAREST);im.save(root/'source-v1.png')
 pixels=im.load();seen=set();boxes=[]
 for y in range(im.height):
  for x in range(im.width):
   if (x,y) in seen or pixels[x,y][3]<160:continue
   todo=[(x,y)];seen.add((x,y));points=[]
   while todo:
    px,py=todo.pop();points.append((px,py))
    for dx,dy in ((-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)):
     nx,ny=px+dx,py+dy
     if 0<=nx<im.width and 0<=ny<im.height and (nx,ny) not in seen and pixels[nx,ny][3]>=160:
      seen.add((nx,ny));todo.append((nx,ny))
   if len(points)<1000:continue
   xs,ys=zip(*points);boxes.append((min(xs),min(ys),max(xs)+1,max(ys)+1))
 assert len(boxes)==12,(slug,len(boxes))
 print(slug,'source bounds',boxes,flush=True)
 assert all(b[0]>0 and b[1]>0 and b[2]<im.width and b[3]<im.height for b in boxes),(slug,'source clipped',boxes)
 meta=next(r for r in roster if r['slug']==slug)
 maximum=max(b[3]-b[1] for b in boxes);width=max(b[2]-b[0] for b in boxes)
 scale=min(1,(meta['reference_size'][1]-1)/maximum,170/width)
 cfg={'source_file':'source-v1.png','source_scale':1,'native_size_source':True,
  'source_size':[724,543],'animal_scale':round(scale,6),'movement':'crouch_pounce',
  'repeat_stand':True,'size_reference':'versions/initial-size-reference'}
 (root/'build-config.json').write_text(json.dumps(cfg,indent=2)+'\n')
 subprocess.run([sys.executable,'reports/build-roster-animality.py',slug],check=True)
 ref=root/'versions/initial-size-reference';ref.mkdir(parents=True,exist_ok=True)
 for f in root.iterdir():
  if f.is_file():shutil.copy2(f,ref/f.name)
