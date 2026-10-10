from pathlib import Path
import sys,json
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image
root=Path('assets/nicotine-animality');m=json.loads((root/'palette-map.json').read_text());lut=m['fbneo_rgb_lut'];pal=Path('reports/nicotine-hat-p1-palette.bin').read_bytes();mask=(root/'hat-palette.bin').read_bytes()
def rgb(i):
 w=int.from_bytes(pal[i*2:i*2+2],'big');return tuple(lut[(w>>s&15)*4+(w>>e&1)*2+(w>>15&1)] for s,e in [(8,14),(4,13),(0,12)])
colors={tuple(c[:3]):c[3] for c in m['colors']};out=Image.new('RGBA',(512,512),(35,42,53,255))
for f in range(16):
 im=Image.open(root/f'frame-{f:02d}.png').convert('RGBA');pixels=[]
 for p,c in enumerate(im.get_flattened_data()):
  if not c[3]:pixels.append(c);continue
  index=mask[f*16384+p]
  if index==255:index=colors[c[:3]]
  if index<48:index=index%16+32
  pixels.append((*rgb(index),255))
 im.putdata(pixels);out.alpha_composite(im,(f%4*128,f//4*128))
out.resize((1024,1024),Image.Resampling.NEAREST).save('reports/owl-hat-pow-reel.png')
