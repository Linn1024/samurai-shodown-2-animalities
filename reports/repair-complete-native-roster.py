"""Install only complete human endpoints; preserve all generated drawings."""
from pathlib import Path
import json,shutil,struct,subprocess,sys
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image
native_root=Path('assets/native-roster')
roster=json.loads((native_root/'roster.json').read_text())
audit=json.loads(Path('reports/complete-native-audit.json').read_text())
backup_root=Path('reports/before-complete-native-roster');backup_root.mkdir(exist_ok=True)
if not (backup_root/'roster.json').exists():shutil.copy2(native_root/'roster.json',backup_root/'roster.json')
results=[]
for r,check in zip(roster,audit):
 slug=r['slug'];assert slug==check['slug'] and not check['removed'] and not check['recolored']
 candidate=Image.open(Path('reports/complete-native-candidates')/(slug+'.png')).convert('RGBA')
 root=Path('assets')/(slug+'-animality')
 current_native=Image.open(root/'native-idle.png' if slug=='ukyo' else native_root/(slug+'.png')).convert('RGBA')
 meta=json.loads((root/'asset-manifest.json').read_text());size=meta['cell'][0];anchor=meta['anchor']
 old_frames=[Image.open(root/f'frame-{i:02d}.png').convert('RGBA') for i in range(16)]
 old_human=old_frames[0];old_box=old_human.getbbox()
 # Ukyo's dedicated original capture has a different crop origin than roster.
 # It can already be complete: compare with matching crop and actor alignment.
 new_anchor=check['anchor']
 canvas=Image.new('RGBA',(size,size))
 canvas.alpha_composite(candidate,(anchor[0]-new_anchor[0],anchor[1]-new_anchor[1]))
 old_pixels={(x-anchor[0],y-anchor[1]):old_human.getpixel((x,y)) for y in range(size) for x in range(size) if old_human.getpixel((x,y))[3]}
 new_pixels={(x-anchor[0],y-anchor[1]):canvas.getpixel((x,y)) for y in range(size) for x in range(size) if canvas.getpixel((x,y))[3]}
 if slug!='ukyo':assert all(new_pixels.get(p)==v for p,v in old_pixels.items()),(slug,'prior installed human pixels changed')
 added=len(new_pixels)-len(old_pixels)
 # Save complete roster reference even if dedicated installed capture was good.
 for name in (slug+'.png',slug+'-reference.png'):
  if not (backup_root/name).exists():shutil.copy2(native_root/name,backup_root/name)
 candidate.save(native_root/(slug+'.png'))
 candidate.resize((candidate.width*6,candidate.height*6),Image.Resampling.NEAREST).save(native_root/(slug+'-reference.png'))
 r.update(reference_size=check['size'],anchor=new_anchor)
 if added or slug=='ukyo':
  backup=root/'versions/before-complete-native-roster';backup.mkdir(parents=True,exist_ok=True)
  for f in root.iterdir():
   if f.is_file() and not (backup/f.name).exists():shutil.copy2(f,backup/f.name)
  if not (backup/'gd').exists():shutil.copytree(root/'gd',backup/'gd')
  box=canvas.getbbox();assert box[0]>0 and box[1]>0 and box[2]<size and box[3]<size,(slug,'clipped')
  canvas.save(root/'frame-00.png');canvas.save(root/'frame-15.png')
  frames=[canvas if i in (0,15) else old_frames[i] for i in range(16)]
  def gd(im):
   data=bytearray(b'\xff\xfe'+struct.pack('>HHBI',im.width,im.height,1,0xffffffff))
   for red,green,blue,alpha in im.get_flattened_data():data.extend((127-round(alpha*127/255),red,green,blue))
   return data
  for direction in ('left','right'):
   sprite=canvas if direction=='right' else canvas.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
   for zoom in (64,80,96,112,128):
    im=sprite if zoom==128 else sprite.resize((size*zoom//128,)*2,Image.Resampling.NEAREST)
    for i in (0,15):(root/'gd'/f'{direction}-{zoom}-{i:02d}.gd').write_bytes(gd(im))
  reel=Image.new('RGBA',(size*4,size*4));preview=[]
  for i,im in enumerate(frames):
   reel.alpha_composite(im,(i%4*size,i//4*size))
   bg=Image.new('RGBA',(size,size),(32,40,56,255));bg.alpha_composite(im);preview.append(bg.convert('RGB').resize((384,384),Image.Resampling.NEAREST))
  reel.save(root/('ukyo-swan-reel.png' if slug=='ukyo' else 'reel.png'))
  preview[0].save(root/('ukyo-swan-preview.gif' if slug=='ukyo' else 'preview.gif'),save_all=True,append_images=preview[1:],duration=100,loop=0,disposal=2)
  # Rebuild only palette maps, without requantizing generated artwork.
  native=candidate
  if slug=='ukyo':
   candidate.save(root/'native-idle.png')
   candidate.resize((candidate.width*6,candidate.height*6),Image.Resampling.NEAREST).save(root/'native-idle-reference.png')
   cfg=json.loads((root/'build-config.json').read_text());cfg['native_anchor']=new_anchor[0]
   (root/'build-config.json').write_text(json.dumps(cfg,indent=2))
   subprocess.run([sys.executable,'reports/build-animality-palette-map.py'],check=True)
  else:
   code=Path('reports/build-roster-animality.py').read_text().split('# Map all native and quantized animal colors',1)[1]
   code=code[:code.index("(root/'asset-manifest.json')")]
   exec('# Map all native and quantized animal colors'+code,dict(root=root,frames=frames,native=native,meta=r,Path=Path,json=json))
  for i in range(1,15):
   assert (root/f'frame-{i:02d}.png').read_bytes()==(backup/f'frame-{i:02d}.png').read_bytes(),(slug,i)
  # Existing resizing references must never resurrect incomplete endpoints.
  cfg=json.loads((root/'build-config.json').read_text())
  for ref in [root/'versions/character-size-cap-reference',root/'versions/human-height-reference',root/cfg.get('size_reference','__none__')]:
   if ref.exists():
    for i in (0,15):
     if (ref/f'frame-{i:02d}.png').exists():shutil.copy2(root/f'frame-{i:02d}.png',ref/f'frame-{i:02d}.png')
 message=f"PASS {slug}: {added} missing installed human pixels restored; generated frames unchanged."
 print(message,flush=True);results.append(dict(slug=slug,restored=added))
(native_root/'roster.json').write_text(json.dumps(roster,indent=2))
Path('reports/complete-native-repair-results.json').write_text(json.dumps(results,indent=2))
