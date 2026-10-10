"""Check packing, clipping, native pixels, and costume rendering after size changes."""
from pathlib import Path
import sys,json,struct,subprocess,re
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image
reviews=json.loads(Path('reports/animality-size-review.json').read_text())
for r in reviews:
 root=Path('assets')/(r['slug']+'-animality');meta=json.loads((root/'asset-manifest.json').read_text());size=meta['cell'][0]
 for index in range(16):
  im=Image.open(root/f'frame-{index:02d}.png').convert('RGBA');b=im.getbbox()
  assert im.size==(size,size) and b and b[0]>0 and b[1]>0 and b[2]<size and b[3]<size,(r['slug'],index,'clipped')
  for z in (64,80,96,112,128):
   for d in ('left','right'):
    gd=(root/'gd'/f'{d}-{z}-{index:02d}.gd').read_bytes();w,h=struct.unpack_from('>HH',gd,2)
    assert gd[:2]==b'\xff\xfe' and (w,h)==(size*z//128,)*2 and len(gd)==11+w*h*4
 assert (root/'frame-00.png').read_bytes()==(root/'frame-15.png').read_bytes()
 print('PASS packed dimensions, unclipped frames and native return: '+r['slug'],flush=True)
roster=json.loads(Path('assets/native-roster/roster.json').read_text());enabled=set(re.findall(r"slug='([^']+)'",Path('animalities.lua').read_text()))
command=[str(Path('tools/HBMAME/hbmame.exe').resolve()),'samsho2s29','-rompath','tools/HBMAME/roms','-pluginspath','tools/HBMAME/plugins','-nvram_directory','reports/test-nvram','-video','none','-sound','none','-nothrottle','-seconds_to_run','10','-console','-skip_gameinfo']
for r in roster:
 if r['slug'] not in enabled:continue
 slug=r['slug'];prefix='nil' if slug=='ukyo' else repr(slug)
 script=f"SS2_TEST_ID={r['id']}; SS2_TEST_PALETTE={r['palette']}; SS2_TEST_SLUG={prefix}; dofile('reports/check-animality-palettes.lua')\n"
 result=subprocess.run(command,input=script,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=45)
 Path(f'reports/resized-{slug}-palette.log').write_text(result.stdout,encoding='utf-8')
 assert result.returncode==0 and '[LUA ERROR]' not in result.stdout and result.stdout.count('sprites rendered and cleared.')==4,slug
 subprocess.run([sys.executable,'reports/verify-animality-palettes.py','--slug',slug],check=True)
 print('PASS resized costume rendering: '+slug,flush=True)
