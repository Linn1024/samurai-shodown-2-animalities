"""Pack imagegen's gauntlet edit, preserving native human and early hybrid."""
from pathlib import Path
import argparse, ast, json, shutil, subprocess, sys
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image, ImageDraw
parser=argparse.ArgumentParser();parser.add_argument('--install',action='store_true');args=parser.parse_args()
root=Path('assets/sieger-animality');stage=Path('reports/sieger-gauntlet-candidate')
if args.install:
 backup=root/'versions/before-gauntlet-v4';backup.mkdir(parents=True,exist_ok=True)
 for f in root.iterdir():
  if f.is_file() and not (backup/f.name).exists():shutil.copy2(f,backup/f.name)
 if not (backup/'gd').exists():shutil.copytree(root/'gd',backup/'gd')
 for f in stage.iterdir():
  if f.is_file():shutil.copy2(f,root/f.name)
 shutil.copytree(stage/'gd',root/'gd',dirs_exist_ok=True)
 baseline=root/'versions/gauntlet-v4-size-reference';baseline.mkdir(parents=True,exist_ok=True)
 for i in range(16):shutil.copy2(root/f'frame-{i:02d}.png',baseline/f'frame-{i:02d}.png')
 shutil.copy2(root/'build-config.json',baseline/'build-config.json')
 print('Installed Sieger gauntlet v4');sys.exit()
stage.mkdir(exist_ok=True)
for f in root.iterdir():
 if f.is_file():shutil.copy2(f,stage/f.name)
g=json.loads(Path('reports/sieger-gauntlet-generation.json').read_text())
for key,name in [('sheet','source-v4'),('morph','idle-morph-v4')]:
 source=Path(g[key]['path'])
 if not source.exists():source=root/(name+'.generated.png')
 shutil.copy2(source,stage/(name+'.generated.png'))
 (stage/('prompt-'+name+'.txt')).write_text(g[key]['prompt'],encoding='utf-8')
sheet=Image.open(stage/'source-v4.generated.png').convert('RGBA')
sheet.resize((723,543),Image.Resampling.NEAREST).save(stage/'source-v4.png')
# Reuse the established alpha/component cleanup, without running its CLI.
tree=ast.parse(Path('reports/prepare-idle-morph-v3.py').read_text())
function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='silhouette')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<silhouette>','exec'))
morph=Image.open(stage/'idle-morph-v4.generated.png').convert('RGBA')
im=silhouette(morph.crop((morph.width//2,0,morph.width,morph.height)))
meta=json.loads((root/'asset-manifest.json').read_text());size=meta['cell'][0];anchor=meta['anchor']
old=Image.open(root/'frame-02.png').convert('RGBA');box=old.getbbox()
target_height=box[3]-box[1];ratio=(anchor[0]-box[0])/(box[2]-box[0])
scale=min(target_height/im.height,(anchor[0]-1)/(im.width*ratio),(size-anchor[0]-1)/(im.width*(1-ratio)))
im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
native=Image.open('assets/native-roster/sieger.png').convert('RGBA')
colors=list(dict.fromkeys(p[:3] for p in native.get_flattened_data() if p[3]))+[(232,248,248),(208,232,240),(168,200,224),(112,144,184),(64,80,128)]
pal=Image.new('P',(1,1));pal.putpalette(sum((list(c) for c in colors),[])+[0]*(768-len(colors)*3))
alpha=im.getchannel('A');im=im.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');im.putalpha(alpha)
canvas=Image.new('RGBA',(size,size));pos=(anchor[0]-round(im.width*ratio),box[3]-im.height);canvas.alpha_composite(im,pos)
canvas.save(stage/'idle-morph-v4-02.png')
cfg=json.loads((root/'build-config.json').read_text())
cfg.update(source_file='source-v4.png',size_reference='versions/gauntlet-v4-size-reference',transformation_overrides=['idle-morph-v3-01.png','idle-morph-v4-02.png'])
(stage/'build-config.json').write_text(json.dumps(cfg,indent=2)+'\n')
subprocess.run([sys.executable,'reports/build-roster-animality.py','sieger','--asset-dir',str(stage)],check=True)
for i in (0,1,14,15):assert (stage/f'frame-{i:02d}.png').read_bytes()==(root/f'frame-{i:02d}.png').read_bytes(),i
for i in range(16):
 im=Image.open(stage/f'frame-{i:02d}.png');b=im.getbbox()
 assert im.size==(192,192) and b[0]>0 and b[1]>0 and b[2]<192 and b[3]<192,(i,b)
assert (stage/'frame-02.png').read_bytes()==(stage/'frame-13.png').read_bytes()
out=Image.new('RGB',(192*4,192*2+24),(35,42,56));d=ImageDraw.Draw(out)
for n,i in enumerate((0,1,2,3,5,7,8,11)):
 im=Image.open(stage/f'frame-{i:02d}.png');pos=(n%4*192,n//4*204+12)
 out.paste(im,pos,im);d.text((pos[0]+4,pos[1]),str(i),fill='white')
out.resize((1536,816),Image.Resampling.NEAREST).save('reports/sieger-gauntlet-review.png')
print('PASS unchanged native human and early hybrid; gauntlet morph returns symmetrically; all frames fit.')
