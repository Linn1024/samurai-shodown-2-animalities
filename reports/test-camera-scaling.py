"""Sweep every camera compression and compare live Lua GD to Pillow NEAREST."""
from pathlib import Path
import json,subprocess,sys
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image
base=Path('reports/check-animality-palettes.lua').read_text()
base=base.replace('for slot=1,2 do','for slot=1,1 do').replace('for variant=0,1 do','for variant=0,0 do')
base=base.replace("for _,zoom in ipairs({64,80,96,112,128}) do","for compression=0,128 do\n local zoom=128-compression/2")
base=base.replace('for frame=0,15 do','for _,frame in ipairs({0,3,8}) do')
base=base.replace(',zoom,frame)',',compression,frame)')
Path('reports/check-camera-scaling.lua').write_text(base)
command=[str(Path('tools/HBMAME/hbmame.exe').resolve()),'samsho2s29','-rompath','tools/HBMAME/roms','-pluginspath','tools/HBMAME/plugins','-nvram_directory','reports/camera-test-nvram','-video','none','-sound','none','-nothrottle','-console','-skip_gameinfo']
log=[]
for slug in ('hanzo','haohmaru','earthquake'):
 r=next(r for r in json.loads(Path('assets/native-roster/roster.json').read_text()) if r['slug']==slug)
 prefix='camera-'+slug
 script=f"SS2_TEST_ID={r['id']};SS2_TEST_PALETTE={r['palette']};SS2_TEST_SLUG='{prefix}';dofile('reports/check-camera-scaling.lua');os.exit()\n"
 result=subprocess.run(command,input=script,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90)
 Path(f'reports/{prefix}-scaling.log').write_text(result.stdout,encoding='utf-8')
 assert result.returncode==0 and '[LUA ERROR]' not in result.stdout,result.stdout[-1200:]
 for direction in ('right','left'):
  for frame in (0,3,8):
   full=Path(f'reports/palette-{prefix}-p1-v0-{direction}-0-{frame:02d}.gd').read_bytes()
   size=int.from_bytes(full[2:4],'big')
   source=Image.frombytes('RGBA',(size,size),full[11:]) # Channels kept as GD ARGB for byte comparison.
   for compression in range(129):
    data=Path(f'reports/palette-{prefix}-p1-v0-{direction}-{compression}-{frame:02d}.gd').read_bytes()
    target=(size*(256-compression)+128)//256
    expected=source.resize((target,target),Image.Resampling.NEAREST).tobytes()
    assert int.from_bytes(data[2:4],'big')==target and len(data)==11+target*target*4
    if data[11:]!=expected:
     # Pillow's floating-point accumulator can choose the lower neighbor at
     # an exact half-pixel tie. Lua deliberately chooses the upper neighbor.
     actual=data[11:]
     for pos in range(0,len(expected),4):
      if actual[pos:pos+4]==expected[pos:pos+4]:continue
      x=pos//4%target;y=pos//4//target
      nx=(2*x+1)*size;ny=(2*y+1)*size
      sx=nx//(2*target);sy=ny//(2*target)
      tie_x=nx%(2*target)==0;tie_y=ny%(2*target)==0
      assert tie_x or tie_y,(slug,compression,x,y,'non-tie mismatch')
      assert actual[pos:pos+4]==full[11+(sy*size+sx)*4:15+(sy*size+sx)*4],(slug,compression,x,y,'wrong original pixel')
 message=f'PASS {slug}: all 129 camera sizes, both directions, human/animal/impact; exact original-pixel nearest-neighbor scaling.'
 log.append(message);print(message,flush=True)
Path('reports/camera-scaling-verification.txt').write_text('\n'.join(log)+'\n')
