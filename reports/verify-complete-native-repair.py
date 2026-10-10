from pathlib import Path
import json,sys
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image,ImageDraw
roster=json.loads(Path('assets/native-roster/roster.json').read_text())
audit={r['slug']:r for r in json.loads(Path('reports/complete-native-audit.json').read_text())}
out=Image.new('RGB',(5*240,4*208),(35,42,56));d=ImageDraw.Draw(out);lines=[];results=[]
for n,r in enumerate(roster):
 slug=r['slug'];root=Path('assets')/(slug+'-animality');meta=json.loads((root/'asset-manifest.json').read_text())
 im=Image.open(root/'frame-00.png').convert('RGBA');native=Image.open(f'reports/complete-native-candidates/{slug}.png').convert('RGBA')
 expected=Image.new('RGBA',im.size);expected.alpha_composite(native,(meta['anchor'][0]-r['anchor'][0],meta['anchor'][1]-r['anchor'][1]))
 assert im.tobytes()==expected.tobytes(),(slug,'complete native endpoint mismatch')
 assert (root/'frame-00.png').read_bytes()==(root/'frame-15.png').read_bytes()
 backup=root/'versions/before-complete-native-roster'
 if backup.exists():
  for i in range(1,15):assert (root/f'frame-{i:02d}.png').read_bytes()==(backup/f'frame-{i:02d}.png').read_bytes(),(slug,i)
  for f in (backup/'gd').glob('*.gd'):
   if not f.name.endswith(('-00.gd','-15.gd')):assert f.read_bytes()==(root/'gd'/f.name).read_bytes(),(slug,f.name)
 restored=audit[slug]['added']
 if slug=='ukyo':message='complete idle recaptured (old dedicated capture included opponent)'
 elif restored:message=f'{restored} missing pixels restored'
 else:message='already complete'
 results.append(dict(slug=slug,result=message,roster_reference_restored=restored))
 lines.append(f'PASS {slug}: {message}; endpoints match opponent-free game capture.')
 b=im.getbbox();crop=im.crop(b);x=n%5*240;y=n//5*208
 d.text((x+5,y+5),r['name'],fill='white');d.text((x+5,y+190),message if slug!='ukyo' else 'complete native idle',fill='white')
 out.paste(crop,(x+(240-crop.width)//2,y+180-crop.height),crop)
Path('reports/complete-native-repair-results.json').write_text(json.dumps(results,indent=2))
Path('reports/complete-native-pixel-verification.txt').write_text('\n'.join(lines)+'\n')
out.save('reports/complete-native-fixed-roster.png')
print('\n'.join(lines))
