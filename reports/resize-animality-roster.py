"""Match animal height to native character height; horizontal length is unrestricted."""
from pathlib import Path
import json,sys,subprocess,shutil
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image,ImageDraw

def bounds(root,i):
 im=Image.open(root/f'frame-{i:02d}.png').convert('RGBA');b=im.getbbox()
 return [b[2]-b[0],b[3]-b[1]]

report=[]
for root in sorted(Path('assets').glob('*-animality')):
 if not (root/'asset-manifest.json').exists():continue
 slug=root.name.removesuffix('-animality')
 human=bounds(root,0)
 before=[bounds(root,i) for i in range(1,15)]
 largest=[max(b[k] for b in before) for k in (0,1)]
 backup=root/'versions/before-character-size-cap'
 backup.mkdir(parents=True,exist_ok=True)
 for f in root.iterdir():
  if f.is_file() and not (backup/f.name).exists():shutil.copy2(f,backup/f.name)
 if not (backup/'gd').exists():shutil.copytree(root/'gd',backup/'gd')
 cfgpath=root/'build-config.json';cfg=json.loads(cfgpath.read_text()) if cfgpath.exists() else {}
 reference=root/cfg.get('size_reference','versions/before-character-size-cap')
 original=[bounds(reference,i) for i in range(1,15)]
 original_max=max(b[1] for b in original)
 original_cfg=json.loads((reference/'build-config.json').read_text())
 original_scale=original_cfg.get('animal_scale',1)
 target=human[1]-1
 previous_scale=cfg.get('animal_scale',1)
 cfg['animal_scale']=round(max(cfg.get('animal_scale',1),original_scale*min(1,target/original_max)),6)
 cfg.pop('contact',None)
 cfgpath.write_text(json.dumps(cfg,indent=2)+'\n')
 commands=[['reports/build-animality-assets.py'],['reports/build-animality-palette-map.py']] if slug=='ukyo' else [['reports/build-roster-animality.py',slug]]
 if cfg['animal_scale']!=previous_scale:
  for command in commands:subprocess.run([sys.executable,*command],check=True)
 after=[bounds(root,i) for i in range(1,15)]
 assert all(b[1]<=max(human[1],largest[1]) for b in after),(slug,human,after)
 for i in (0,15):assert (root/f'frame-{i:02d}.png').read_bytes()==(backup/f'frame-{i:02d}.png').read_bytes(),slug
 report.append({'slug':slug,'human':human,'before_max':largest,'after_max':[max(b[k] for b in after) for k in (0,1)],'animal_scale':cfg['animal_scale']})
 print(slug,largest,'->',report[-1]['after_max'],'human',human,flush=True)
Path('reports/animality-character-size-cap.json').write_text(json.dumps(report,indent=2)+'\n')
subprocess.run([sys.executable,'reports/build-roster-registry.py','--existing-only'],check=True)
out=Image.new('RGB',(1600,((len(report)+3)//4)*210),(32,40,56));draw=ImageDraw.Draw(out)
for index,r in enumerate(report):
 root=Path('assets')/(r['slug']+'-animality');x=(index%4)*400;y=(index//4)*210
 draw.text((x+6,y+6),r['slug'],fill='white')
 for col,frame in enumerate((0,8)):
  im=Image.open(root/f'frame-{frame:02d}.png').convert('RGBA');im=im.crop(im.getbbox())
  out.paste(im,(x+col*200+(200-im.width)//2,y+160-im.height),im)
 draw.text((x+6,y+174),f"Human {r['human']}\nAnimal max {r['after_max']}",fill='white')
preview_path=Path('reports/animality-human-height-comparison.png')
try:out.save(preview_path)
except OSError:
 from datetime import datetime
 preview_path=preview_path.with_stem(preview_path.stem+'-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
 out.save(preview_path)
print('Comparison:',preview_path)
