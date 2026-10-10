from pathlib import Path
import sys,shutil,struct,json
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image
root=Path('assets/galford-animality');stage=Path('reports/galford-cleanup-candidate')
for i in (0,15):
 assert (root/f'frame-{i:02d}.png').read_bytes()==(stage/f'frame-{i:02d}.png').read_bytes()
assert (stage/'frame-03.png').read_bytes()==(stage/'frame-12.png').read_bytes()
for i in range(16):
 im=Image.open(stage/f'frame-{i:02d}.png').convert('RGBA');box=im.getbbox()
 assert im.size==(192,192) and box[0]>0 and box[1]>0 and box[2]<192 and box[3]<192
 assert set(im.getchannel('A').getdata()) <= {0,255}
 old=Image.open(root/f'frame-{i:02d}.png').getbbox()
 assert abs((box[2]-box[0])-(old[2]-old[0]))<=8,(i,box,old)
 assert abs((box[3]-box[1])-(old[3]-old[1]))<=8,(i,box,old)
for f in (stage/'gd').glob('*.gd'):
 data=f.read_bytes();w,h=struct.unpack_from('>HH',data,2)
 assert data[:2]==b'\xff\xfe' and len(data)==11+w*h*4
assert len(list((stage/'gd').glob('*.gd')))==160
backup=root/'versions/before-detail-cleanup-v4';backup.mkdir(parents=True,exist_ok=True)
for f in root.iterdir():
 if f.is_file() and not (backup/f.name).exists():shutil.copy2(f,backup/f.name)
if not (backup/'gd').exists():shutil.copytree(root/'gd',backup/'gd')
for f in stage.iterdir():
 if f.is_file():shutil.copy2(f,root/f.name)
shutil.copytree(stage/'gd',root/'gd',dirs_exist_ok=True)
print('PASS 16 unclipped frames, 160 packed sprites, binary alpha, unchanged human frames, repeated stand and size tolerance; installed v4 with backup.')
