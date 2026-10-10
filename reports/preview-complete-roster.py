from pathlib import Path
import sys,json
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image,ImageDraw
roster=json.loads(Path('assets/native-roster/roster.json').read_text())
out=Image.new('RGB',(1600,((len(roster)+3)//4)*210),(32,40,56));d=ImageDraw.Draw(out)
sizes=[]
for i,r in enumerate(roster):
 root=Path('assets')/(r['slug']+'-animality');x=(i%4)*400;y=(i//4)*210
 d.text((x+8,y+7),r['name']+' / '+r['animal'],fill='white')
 for col,frame in enumerate((0,3)):
  im=Image.open(root/f'frame-{frame:02d}.png').convert('RGBA');b=im.getbbox();im=im.crop(b)
  out.paste(im,(x+col*200+(200-im.width)//2,y+164-im.height),im)
 d.text((x+8,y+177),'Native human                     Animal readiness',fill='white')
 sizes.append({'slug':r['slug'],'config':json.loads((root/'build-config.json').read_text())})
out.save('reports/complete-animality-roster.png')
Path('reports/complete-animality-roster-sizes.json').write_text(json.dumps(sizes,indent=2)+'\n')
