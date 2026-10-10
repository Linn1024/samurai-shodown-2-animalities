from pathlib import Path
import sys,struct,json
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image,ImageDraw
def read(path):
 data=Path(path).read_bytes();w,h=struct.unpack_from('>HH',data,2);rgba=bytearray()
 for p in range(11,len(data),4):
  a,r,g,b=data[p:p+4];rgba.extend((r,g,b,255-round(a*255/127)))
 return Image.frombytes('RGBA',(w,h),bytes(rgba))
out=Image.new('RGBA',(640,480),(32,40,56,255));draw=ImageDraw.Draw(out)
mapping=json.loads(Path('assets/gen-an-animality/palette-map.json').read_text());lut=mapping['fbneo_rgb_lut']
def rgb(w):
 dark=w>>15&1
 return tuple(lut[v] for v in ((w>>8&15)*4+(w>>14&1)*2+dark,(w>>4&15)*4+(w>>13&1)*2+dark,(w&15)*4+(w>>12&1)*2+dark))
for slot in (1,2):
 y=(slot-1)*240;native=read(f'reports/genan-live-banks-p{slot}-native.gd')
 animal=read(f'reports/genan-live-banks-p{slot}-animal.gd')
 out.alpha_composite(native,(0,y+16));out.alpha_composite(animal,((320+(320-animal.width)//2),y+230-animal.height))
 palette=Path(f'reports/genan-live-banks-p{slot}-palette.bin').read_bytes()
 skin={rgb(int.from_bytes(palette[i:i+2],'big')) for i in range(64,96,2)}
 visible=[p[:3] for p in animal.get_flattened_data() if p[3]]
 # Orange full-POW skin appears in the actual overlaid animal, not purple base.
 assert sum(c in skin and c[0]>c[2]*2 and c[0]>c[1] for c in visible)>50,slot
 draw.text((4,y+2),f'P{slot}: native alternate Gen-an, full POW',fill='white')
 draw.text((340,y+2),'Animal follows live POW bank',fill='white')
out.convert('RGB').resize((1280,960),Image.Resampling.NEAREST).save('reports/genan-live-bank-comparison.png')
print('PASS actual FBNeo Gen-an: orange native POW skin appears on bat in both player slots.')
