"""Reusable 12-cell source -> 16-frame animality builder and costume map.
Uses native captures in assets/native-roster. Existing Ukyo assets are left alone.
"""
from pathlib import Path
import argparse,json,sys,struct
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image

args=argparse.ArgumentParser()
args.add_argument('slug');args.add_argument('--scale',type=float)
args.add_argument('--asset-dir',type=Path,help='Build a review candidate without replacing installed assets')
args=args.parse_args()
meta=next(r for r in json.loads(Path('assets/native-roster/roster.json').read_text()) if r['slug']==args.slug)
root=args.asset_dir or Path('assets')/(args.slug+'-animality');root.mkdir(exist_ok=True)
config_path=root/'build-config.json'
config=json.loads(config_path.read_text()) if config_path.exists() else {}
args.scale=args.scale if args.scale is not None else config.get('source_scale',.22)
native=Image.open(Path('assets/native-roster')/(args.slug+'.png')).convert('RGBA')
source_file=config.get('source_file','source-v1.png')
source=Image.open(root/source_file).convert('RGBA')
if config.get('native_size_source'):
 assert args.scale==1,('A native-size drawing must not be enlarged',args.scale)
 assert list(source.size)==config['source_size'],('Native-size source dimensions changed',source.size)
animal_scale=config.get('animal_scale',1)
assert 0<animal_scale<=1
display_scale=args.scale*animal_scale
source.putdata([(r,g,b,255) if a>=160 else (0,0,0,0) for r,g,b,a in source.get_flattened_data()])
canvas_size=config.get('canvas_size',128)
while True:
 anchor=(canvas_size//2,canvas_size-16)
 ax,ay=meta['anchor']
 if ax<=anchor[0] and ay<=anchor[1] and native.width-ax<=canvas_size-anchor[0] and native.height-ay<=16:break
 canvas_size+=64
# Connected silhouettes avoid chopping paws/tails when generated grid borders drift.
pixels=source.load();seen=set();components=[]
for y in range(source.height):
 for x in range(source.width):
  if (x,y) in seen or not pixels[x,y][3]:continue
  todo=[(x,y)];seen.add((x,y));points=[]
  while todo:
   px,py=todo.pop();points.append((px,py))
   for dx,dy in ((-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)):
    nx,ny=px+dx,py+dy
    if 0<=nx<source.width and 0<=ny<source.height and (nx,ny) not in seen and pixels[nx,ny][3]:
     seen.add((nx,ny));todo.append((nx,ny))
  if len(points)>=1000:
   xs,ys=zip(*points);components.append(((min(xs),min(ys),max(xs)+1,max(ys)+1),points))
assert len(components)==12,('Expected 12 complete sprite silhouettes',len(components))
components.sort(key=lambda item:(int(((item[0][1]+item[0][3])/2)/(source.height/3)),item[0][0]))
# Fit every enlarged animal pose as well as the unscaled native human.
while any(round(round((b[2]-b[0])*display_scale)*.55)>canvas_size//2 or
          round((b[2]-b[0])*display_scale)-round(round((b[2]-b[0])*display_scale)*.55)>canvas_size//2 or
          round((b[3]-b[1])*display_scale)>canvas_size-16 for b,_ in components):
 canvas_size+=64
anchor=(canvas_size//2,canvas_size-16)
palette_colors=list(dict.fromkeys(p[:3] for p in native.get_flattened_data() if p[3]))
palette_colors += [(232,248,248),(208,232,240),(168,200,224),(112,144,184),(64,80,128)]
pal=Image.new('P',(1,1));pal.putpalette(sum((list(p) for p in palette_colors),[])+[0]*(768-3*len(palette_colors)))
def canvas(im,anchor):
 out=Image.new('RGBA',(canvas_size,canvas_size));pos=(canvas_size//2-anchor[0],canvas_size-16-anchor[1])
 assert pos[0]>=0 and pos[1]>=0 and pos[0]+im.width<=canvas_size and pos[1]+im.height<=canvas_size,('Sprite exceeds canvas',im.size,pos)
 out.alpha_composite(im,pos);return out
frames=[canvas(native,meta['anchor'])]
for box,points in components:
 im=Image.new('RGBA',(box[2]-box[0],box[3]-box[1]))
 target=im.load()
 for x,y in points:target[x-box[0],y-box[1]]=pixels[x,y]
 im=im.resize((round(im.width*display_scale),round(im.height*display_scale)),Image.Resampling.NEAREST)
 alpha=im.getchannel('A');im=im.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');im.putalpha(alpha)
 frames.append(canvas(im,(round(im.width*.55),im.height)))
if config.get('repeat_stand'):frames[12]=frames[3].copy()
# Optional separately authored early/late morphs; attack drawings stay unchanged.
# These are already normalized to the shared canvas and palette by the importer.
if config.get('transformation_overrides'):
 assert len(config['transformation_overrides'])==2
 for index,file in enumerate(config['transformation_overrides'],1):
  im=Image.open(root/file).convert('RGBA')
  assert im.size==(canvas_size,canvas_size),(file,'override canvas mismatch')
  assert set(im.getchannel('A').get_flattened_data())<={0,255}
  assert all(p[:3] in palette_colors for p in im.get_flattened_data() if p[3]),file
  frames[index]=im
frames.extend([frames[2].copy(),frames[1].copy(),frames[0].copy()])
assert len(frames)==16
reel=Image.new('RGBA',(canvas_size*4,canvas_size*4))
for i,im in enumerate(frames):
 im.save(root/f'frame-{i:02d}.png');reel.alpha_composite(im,((i%4)*canvas_size,(i//4)*canvas_size))
reel.save(root/'reel.png')
def gd(im):
 data=bytearray(b'\xff\xfe'+struct.pack('>HHBI',im.width,im.height,1,0xffffffff))
 for r,g,b,a in im.get_flattened_data():data.extend((127-round(a*127/255),r,g,b))
 return bytes(data)
packed=root/'gd';packed.mkdir(exist_ok=True)
for zoom in (64,80,96,112,128):
 for direction in ('right','left'):
  for index,im in enumerate(frames):
   sprite=im if direction=='right' else im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
   if zoom!=128:sprite=sprite.resize((canvas_size*zoom//128,canvas_size*zoom//128),Image.Resampling.NEAREST)
   (packed/f'{direction}-{zoom}-{index:02d}.gd').write_bytes(gd(sprite))
preview=[]
for im in frames:
 bg=Image.new('RGBA',(canvas_size,canvas_size),(32,40,56,255));bg.alpha_composite(im)
 preview.append(bg.convert('RGB').resize((384,384),Image.Resampling.NEAREST))
preview[0].save(root/'preview.gif',save_all=True,append_images=preview[1:],duration=[100,100,100,100,80,80,80,80,120,100,100,100,100,100,100,180],loop=0,disposal=2)
# Map all native and quantized animal colors to this fighter's 128 palette entries.
rom=bytearray(Path('work/hack/063sp.p2').read_bytes());rom[0::2],rom[1::2]=rom[1::2],rom[0::2]
offset=meta['palette']-0x200000
words=[int.from_bytes(rom[a:a+2],'big') for a in range(offset,offset+256,2)]
def lut(resistors):
 weights=[255/r/sum(1/x for x in resistors) for r in resistors]
 return [int(sum(w*((v>>i)&1) for i,w in enumerate(weights))+.5) for v in range(1<<len(weights))]
hb=lut([3900,2200,1000,470,220]);fb=lut([8200,3900,2200,1000,470,220])
def native_rgb(w):return tuple(hb[v] for v in [(w>>8&15)*2+(w>>14&1),(w>>4&15)*2+(w>>13&1),(w&15)*2+(w>>12&1)])
native_colors=[native_rgb(w) for w in words]
used=sorted({p[:3] for im in frames for p in im.get_flattened_data() if p[3]})
mapping=[]
for color in used:
 index=min((i for i in range(128) if i%16),key=lambda i:sum((color[k]-native_colors[i][k])**2 for k in range(3)))
 mapping.append([*color,index,words[index]])
human_colors={p[:3] for p in native.get_flattened_data() if p[3]}
assert all(c in native_colors for c in human_colors),('Native capture colors do not match ROM palette',human_colors-set(native_colors))
(root/'palette-map.lua').write_text('-- Generated by reports/build-roster-animality.py\nreturn {rgb={'+','.join(map(str,fb))+'},colors={\n'+''.join(' {'+','.join(map(str,row))+'},\n' for row in mapping)+'}}\n')
(root/'palette-map.json').write_text(json.dumps({'source_palette':meta['palette'],'colors':mapping,'human_colors_exact':len(human_colors),'fbneo_rgb_lut':fb},indent=2))
(root/'asset-manifest.json').write_text(json.dumps({'character':meta,'frames':16,'cell':[canvas_size,canvas_size],'anchor':list(anchor),'source_scale':args.scale,'source':'native capture + image_gen '+source_file,'source_file':source_file,'source_boxes':[item[0] for item in components],'transformation_overrides':config.get('transformation_overrides',[]),'zooms':[64,80,96,112,128]},indent=2))
print(f"Built {meta['name']} {meta['animal']}: 16 frames, 160 GD sprites, {len(human_colors)} exact native colors.")
