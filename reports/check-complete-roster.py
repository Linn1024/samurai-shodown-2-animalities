from pathlib import Path
import sys,json,struct,subprocess,re,argparse
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image
roster=json.loads(Path('assets/native-roster/roster.json').read_text())
assert len(roster)==17
enabled=set(re.findall(r"slug='([^']+)'",Path('animalities.lua').read_text()))
assert enabled=={r['slug'] for r in roster}
parser=argparse.ArgumentParser();parser.add_argument('--slugs',nargs='+');parser.add_argument('--report',default='reports/complete-roster-verification.txt');args=parser.parse_args()
if args.slugs:
 assert set(args.slugs)<={r['slug'] for r in roster}
 roster=[r for r in roster if r['slug'] in args.slugs]
log=[]
command=[str(Path('tools/HBMAME/hbmame.exe').resolve()),'samsho2s29','-rompath','tools/HBMAME/roms','-pluginspath','tools/HBMAME/plugins','-nvram_directory','reports/palette-test-nvram','-video','none','-sound','none','-nothrottle','-seconds_to_run','10','-console','-skip_gameinfo']
for r in roster:
 slug=r['slug'];root=Path('assets')/(slug+'-animality')
 meta=json.loads((root/'asset-manifest.json').read_text());size=meta['cell'][0]
 assert len(list((root/'gd').glob('*.gd')))==160
 for i in range(16):
  im=Image.open(root/f'frame-{i:02d}.png').convert('RGBA');b=im.getbbox()
  assert im.size==(size,size) and b[0]>0 and b[1]>0 and b[2]<size and b[3]<size,(slug,i,'clipped')
  assert set(im.getchannel('A').get_flattened_data())<={0,255}
  for direction in ('left','right'):
   for zoom in (64,80,96,112,128):
    data=(root/'gd'/f'{direction}-{zoom}-{i:02d}.gd').read_bytes();w,h=struct.unpack_from('>HH',data,2)
    assert data[:2]==b'\xff\xfe' and (w,h)==(size*zoom//128,)*2 and len(data)==11+4*w*h
 native=Image.open(root/'native-idle.png' if slug=='ukyo' else Path('assets/native-roster')/(slug+'.png')).convert('RGBA')
 human=Image.open(root/'frame-00.png').convert('RGBA')
 assert human.crop(human.getbbox()).tobytes()==native.crop(native.getbbox()).tobytes(),slug
 assert (root/'frame-00.png').read_bytes()==(root/'frame-15.png').read_bytes(),slug
 prefix='nil' if slug=='ukyo' else repr(slug)
 script=f"SS2_TEST_ID={r['id']}; SS2_TEST_PALETTE={r['palette']}; SS2_TEST_SLUG={prefix}; dofile('reports/check-animality-palettes.lua')\n"
 result=subprocess.run(command,input=script,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
 Path(f'reports/complete-{slug}-palette.log').write_text(result.stdout,encoding='utf-8')
 assert result.returncode==0 and '[LUA ERROR]' not in result.stdout and result.stdout.count('sprites rendered and cleared.')==4,slug
 subprocess.run([sys.executable,'reports/verify-animality-palettes.py','--slug',slug],check=True)
 message=f'PASS {slug}: 16 unclipped frames, exact native human, 160 GD assets, 640 costume variants.'
 log.append(message);print(message,flush=True)
 Path(args.report).write_text('\n'.join(log)+'\n')
