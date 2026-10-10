"""Run fresh native-game integration checks for each enabled animality."""
from pathlib import Path
import argparse,json,re,subprocess,sys
parser=argparse.ArgumentParser();parser.add_argument('slugs',nargs='*');parser.add_argument('--modes',nargs='+',default=['default','left','p2','normal','cancel']);parser.add_argument('--force-finish',action='store_true');args=parser.parse_args()
roster=json.loads(Path('assets/native-roster/roster.json').read_text())
selected=[r for r in roster if not args.slugs or r['slug'] in args.slugs]
assert selected
command=[str(Path('tools/HBMAME/hbmame.exe').resolve()),'samsho2s29','-rompath','tools/HBMAME/roms','-pluginspath','tools/HBMAME/plugins','-nvram_directory','reports/test-nvram','-video','none','-sound','none','-nothrottle','-seconds_to_run','75','-console','-skip_gameinfo']
checks=[]
try:
 for character in selected:
  slug=character['slug']
  for mode in args.modes:
   Path('reports/animality-test-config.txt').write_text('' if mode=='default' else mode)
   script=f"SS2_TEST_ID={character['id']}; SS2_TEST_FORCE_FINISH={'true' if args.force_finish else 'false'}; SS2_TEST_CAPTURE={'true' if mode=='default' else 'false'}; dofile('reports/test-animality.lua')\n"
   result=subprocess.run(command,input=script,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=45)
   log=Path(f'reports/test-{slug}-animality-{mode}.log');log.write_text(result.stdout,encoding='utf-8')
   assert result.returncode==0 and '[LUA ERROR]' not in result.stdout and 'ANIMALITY ERROR' not in result.stdout,(slug,mode,result.stdout[-1600:])
   events=0 if mode=='normal' else 1
   assert f'ANIMALITY TEST events={events} active=false handler=25314' in result.stdout,(slug,mode,result.stdout[-1600:])
   if mode in ('default','left'):
    assert 'human form restored; native victory pose.' in result.stdout,(slug,mode)
    # Direct death-state fixtures do not set the native lethal-hit round counter.
    if not args.force_finish:assert re.search(r'CONTINUE p1=[a-f0-9]+ hp=128 state=0 p2hp=128',result.stdout),(slug,mode,result.stdout[-1800:])
   if mode=='cancel':assert 'cancelled:' in result.stdout,(slug,mode)
   if mode=='default':
    subprocess.run([sys.executable,'reports/preview-animality-game.py','--slug',slug],check=True,stdout=subprocess.DEVNULL)
   checks.append(f'PASS {slug}: {mode}, events={events}, no active sequence, native callback restored.')
   print(checks[-1],flush=True)
finally:
 Path('reports/animality-test-config.txt').write_text('')
 Path('reports/roster-native-verification.txt').write_text('\n'.join(checks)+'\n')
