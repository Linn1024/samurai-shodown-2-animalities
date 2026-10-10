from pathlib import Path
import sys,json,shutil
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image
stage=Path('reports/galford-fresh-candidate');stage.mkdir(exist_ok=True)
generated=Path('C:/Users/linn1/.codex/generated_images/01a12259-5416-7c60-8115-a389a45534d0/exec-71e50b2e-f11a-4ee2-94b9-8bd8ed91faf9.png')
im=Image.open(generated).convert('RGBA');assert im.size==(1448,1086),im.size
shutil.copy2(generated,stage/'source-v5.generated.png')
im=im.resize((724,543),Image.Resampling.NEAREST)
im.save(stage/'source-v5.png')
alpha=im.getchannel('A').point(lambda x:255 if x>=160 else 0)
heights=[];seen=set();pixels=alpha.load()
for y in range(alpha.height):
 for x in range(alpha.width):
  if (x,y) in seen or not pixels[x,y]:continue
  todo=[(x,y)];seen.add((x,y));points=[]
  while todo:
   px,py=todo.pop();points.append((px,py))
   for dx,dy in ((-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)):
    nx,ny=px+dx,py+dy
    if 0<=nx<alpha.width and 0<=ny<alpha.height and (nx,ny) not in seen and pixels[nx,ny]:
     seen.add((nx,ny));todo.append((nx,ny))
  if len(points)<1000:continue
  xs,ys=zip(*points)
  assert min(xs)>0 and min(ys)>0 and max(xs)<alpha.width-1 and max(ys)<alpha.height-1
  heights.append(max(ys)-min(ys)+1)
assert len(heights)==12,len(heights)
cfg={'source_file':'source-v5.png','source_scale':1,'native_size_source':True,
 'source_size':[724,543],'animal_scale':round(min(1,108/max(heights)),6),
 'movement':'crouch_pounce','repeat_stand':True,
 'size_reference':'versions/fresh-v5-size-reference'}
(stage/'build-config.json').write_text(json.dumps(cfg,indent=2)+'\n')
shutil.copy2('reports/galford-fresh-source-prompt.txt',stage/'prompt-v5.txt')
print('Source heights:',heights,'display scale:',cfg['animal_scale'])
