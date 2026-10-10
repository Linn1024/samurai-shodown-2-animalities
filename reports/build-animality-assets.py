"""Build emulator assets from the generated reel and unchanged native poses.
Cropping, alpha cleanup, palette conversion and packing only; no drawn replacement art.
"""
from pathlib import Path
import sys,struct,json
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image

root=Path('assets/ukyo-animality')
config=json.loads((root/'build-config.json').read_text()) if (root/'build-config.json').exists() else {}
source_scale=config.get('source_scale',.22)
animal_scale=config.get('animal_scale',1)
assert 0<animal_scale<=1
canvas_size=config.get('canvas_size',128)
origin=(canvas_size//2,canvas_size-16)
sheet=Image.open(root/'swan-source-v2.png').convert('RGBA')
print('Source',sheet.size)
cellw,cellh=sheet.width//4,sheet.height//3
frames=[]
native=Image.open(root/'native-idle.png').convert('RGBA')
# A single shared palette from Ukyo's native pixels + swan ivory shades.
palette_colors=list(dict.fromkeys(p[:3] for p in native.get_flattened_data() if p[3]))
palette_colors += [(232,248,248),(208,232,240),(168,200,224),(112,144,184),(64,80,128)]
pal=Image.new('P',(1,1)); pal.putpalette(sum((list(p) for p in palette_colors),[])+[0]*(768-3*len(palette_colors)))

def normalize(im,scale=1,anchor=None):
    # Remove isolated low-alpha edge noise before reducing to the game's pixels.
    im.putdata([(r,g,b,255) if a>=160 else (0,0,0,0) for r,g,b,a in im.get_flattened_data()])
    # Sprite-sheet cells can contain stray feather pixels from adjacent cells.
    # Keep the principal connected shape and substantial nearby feather effects.
    if scale!=1:
        pixels=im.load(); seen=set(); components=[]
        for yy in range(im.height):
            for xx in range(im.width):
                if (xx,yy) in seen or pixels[xx,yy][3]==0: continue
                todo=[(xx,yy)]; seen.add((xx,yy)); component=[]
                while todo:
                    x,y=todo.pop(); component.append((x,y))
                    for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                        if 0<=nx<im.width and 0<=ny<im.height and (nx,ny) not in seen and pixels[nx,ny][3]:
                            seen.add((nx,ny));todo.append((nx,ny))
                components.append(component)
        for component in components:
            if len(component)<45:
                for x,y in component: pixels[x,y]=(0,0,0,0)
    box=im.getbbox()
    assert box
    im=im.crop(box)
    if scale!=1: im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
    alpha=im.getchannel('A')
    rgb=im.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA')
    rgb.putalpha(alpha)
    out=Image.new('RGBA',(canvas_size,canvas_size))
    # Native origin is the game's projected actor position; swan origin tracks its breast.
    ax=anchor if anchor is not None else round(im.width*.55)
    pos=(origin[0]-ax,origin[1]-im.height)
    assert pos[0]>=0 and pos[1]>=0 and pos[0]+rgb.width<=canvas_size and pos[1]+rgb.height<=canvas_size,('Sprite exceeds canvas',rgb.size,pos)
    out.alpha_composite(rgb,pos)
    return out

native_frame=normalize(native,anchor=config.get('native_anchor',45))
frames.append(native_frame)
for index in range(12):
    c,r=index%4,index//4
    im=sheet.crop((c*cellw,r*cellh,(c+1)*cellw,(r+1)*cellh))
    frames.append(normalize(im,source_scale*animal_scale))
# Reverse exactly the same transformation drawings to avoid an inconsistent return.
frames.extend([frames[2].copy(),frames[1].copy(),native_frame.copy()])
assert len(frames)==16
atlas=Image.new('RGBA',(canvas_size*4,canvas_size*4))
for i,im in enumerate(frames):
    im.save(root/f'frame-{i:02d}.png')
    atlas.alpha_composite(im,((i%4)*canvas_size,(i//4)*canvas_size))
atlas.save(root/'ukyo-swan-reel.png')

def gd(im):
    data=bytearray(b'\xff\xfe'+struct.pack('>HHBI',im.width,im.height,1,0xffffffff))
    for r,g,b,a in im.get_flattened_data(): data.extend((127-round(a*127/255),r,g,b))
    return bytes(data)

# Pre-scale and mirror once, never resample the sprite every emulator frame.
packed=root/'gd'; packed.mkdir(exist_ok=True)
for zoom in (64,80,96,112,128):
    for direction in ('right','left'):
        for index,im in enumerate(frames):
            sprite=im if direction=='right' else im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if zoom!=128: sprite=sprite.resize((canvas_size*zoom//128,canvas_size*zoom//128),Image.Resampling.NEAREST)
            (packed/f'{direction}-{zoom}-{index:02d}.gd').write_bytes(gd(sprite))

durations=[100,80,80,100,80,80,80,80,100,90,90,90,100,80,80,180]
preview=[]
for im in frames:
    bg=Image.new('RGBA',(canvas_size,canvas_size),(32,40,56,255));bg.alpha_composite(im)
    preview.append(bg.convert('RGB').resize((384,384),Image.Resampling.NEAREST))
preview[0].save(root/'ukyo-swan-preview.gif',save_all=True,append_images=preview[1:],duration=durations,loop=0,disposal=2)
(root/'asset-manifest.json').write_text(json.dumps({'frames':16,'cell':[canvas_size,canvas_size],'anchor':list(origin),'source_scale':source_scale,'native_human_frames':[0,15],'source':'native emulator capture + built-in image_gen swan-source-v2.png','palette_colors':len(palette_colors),'mirror':True,'zooms':[64,80,96,112,128]},indent=2))
print('Built 16 aligned frames, mirrored GD assets and GIF preview.')
