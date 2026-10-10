from pathlib import Path
import argparse
import sys,struct
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image
frames=[]
parser=argparse.ArgumentParser();parser.add_argument('--slug',default='ukyo');args=parser.parse_args()
paths=[p for p in Path('reports').glob('animality-game-*.png') if p.stem.rsplit('-',1)[1].isdigit()]
for path in sorted(paths,key=lambda p:int(p.stem.rsplit('-',1)[1])):
    im=Image.open(path).convert('RGBA')
    data=path.with_suffix('.gd')
    if data.exists():
        b=data.read_bytes();w,h=struct.unpack_from('>HH',b,2)
        rgba=bytearray()
        for a,r,g,bl in zip(b[11::4],b[12::4],b[13::4],b[14::4]):rgba.extend((r,g,bl,255-round(a*255/127)))
        overlay=Image.frombytes('RGBA',(w,h),bytes(rgba))
        x,y=map(int,path.with_suffix('.xy').read_text().split())
        im.alpha_composite(overlay,(x,y))
    im.save(path.with_name(path.stem+'-composite.png'))
    frames.append(im.convert('RGB').resize((640,448),Image.Resampling.NEAREST))
frames[0].save(f'assets/{args.slug}-animality/in-game-preview.gif',save_all=True,append_images=frames[1:],duration=166,loop=0)
print(len(frames),'emulated game frames with the same GD overlay used by FBNeo')
