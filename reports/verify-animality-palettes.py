from pathlib import Path
import json,struct,sys,argparse
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image,ImageDraw
parser=argparse.ArgumentParser();parser.add_argument('--slug',default='ukyo');args=parser.parse_args()
root=Path('assets')/(args.slug+'-animality')
mapping=json.loads((root/'palette-map.json').read_text())
rom=bytearray(Path('work/hack/063sp.p2').read_bytes())
rom[0::2],rom[1::2]=rom[1::2],rom[0::2]
lut=mapping['fbneo_rgb_lut']
def rgb(w):
    d=w>>15&1
    return bytes(lut[v] for v in [(w>>8&15)*4+(w>>14&1)*2+d,(w>>4&15)*4+(w>>13&1)*2+d,(w&15)*4+(w>>12&1)*2+d])
count=0
prefix='palette' if args.slug=='ukyo' else 'palette-'+args.slug
source=0x214600 if args.slug=='ukyo' else mapping['source_palette']
for path in Path('reports').glob(prefix+'-p*-v*-*.gd'):
    slot,variant,direction,zoom,frame=path.stem[len(prefix)+1:].split('-')
    variant=int(variant[1:]);base=source-0x200000+variant*256
    replacements={bytes([0,*entry[:3]]):bytes([0])+rgb(int.from_bytes(rom[base+entry[3]*2:base+entry[3]*2+2],'big')) for entry in mapping['colors']}
    original=(root/'gd'/f'{direction}-{zoom}-{frame}.gd').read_bytes()
    result=path.read_bytes()
    assert original[:11]==result[:11] and len(original)==len(result),path
    for i in range(11,len(original),4):
        pixel=original[i:i+4]
        assert result[i:i+4]==replacements.get(pixel,pixel),(path,i)
    count+=1
assert count==640,count
sample=Path(f'reports/{prefix}-p1-v0-right-128-00.gd').read_bytes()
cell=struct.unpack_from('>H',sample,2)[0]
canvas=Image.new('RGB',(cell*6,(cell+20)*2),(32,40,56));draw=ImageDraw.Draw(canvas)
for variant in (0,1):
    draw.text((8,variant*(cell+20)+4),'Default costume' if variant==0 else 'Alternate costume',fill='white')
    for col,frame in enumerate([0,2,6,8,13,15]):
        data=Path(f'reports/{prefix}-p1-v{variant}-right-128-{frame:02d}.gd').read_bytes()
        rgba=bytearray()
        for i in range(11,len(data),4):
            a,r,g,b=data[i:i+4];rgba.extend((r,g,b,255-round(a*255/127)))
        im=Image.frombytes('RGBA',(cell,cell),bytes(rgba))
        canvas.paste(im,(col*cell,variant*(cell+20)+20),im)
canvas.resize((1536,592),Image.Resampling.NEAREST).save(root/'costume-palettes-preview.png')
message='PASS: 640 runtime GD sprites, two costumes, both players, both directions and all five sizes; every color, alpha byte and header verified.\n'
Path(f'reports/{args.slug}-animality-palette-verification.txt').write_text(message)
print(message)
