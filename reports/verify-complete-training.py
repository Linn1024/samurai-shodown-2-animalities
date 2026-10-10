from pathlib import Path
import subprocess,json,sys
subprocess.run([sys.executable,'reports/build-roster-registry.py','--output','reports/animalities-all-built.lua'],check=True)
command=[str(Path('tools/HBMAME/hbmame.exe').resolve()),'samsho2s29','-rompath','tools/HBMAME/roms','-pluginspath','tools/HBMAME/plugins','-nvram_directory','reports/training-test-nvram','-video','none','-sound','none','-nothrottle','-console','-skip_gameinfo']
script="dofile('reports/check-training.lua'); dofile('reports/check-training-switch.lua'); dofile('reports/check-animality-waiting.lua'); os.exit()\n"
r=subprocess.run(command,input=script,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=45)
Path('reports/complete-training-guard-verification.log').write_text(r.stdout,encoding='utf-8')
assert r.returncode==0 and '[LUA ERROR]' not in r.stdout and 'PASS character switching:' in r.stdout and 'PASS all 17 built animals:' in r.stdout,r.stdout[-2000:]
for line in r.stdout.splitlines():
 if line.startswith('PASS'):print(line)
lines=[]
for row in json.loads(Path('assets/native-roster/roster.json').read_text()):
 text=Path(f"reports/test-{row['slug']}-animality-default.log").read_text(encoding='utf-8')
 assert 'ANIMALITY TEST events=1 active=false handler=25314' in text and 'human form restored; native victory pose.' in text,row['slug']
 mode='direct native death state' if 'SS2_TEST_FORCE_FINISH=true' in text else 'native attack KO'
 lines.append(f"PASS {row['slug']}: native fountain, animality, human victory, callback restored; fixture={mode}.")
Path('reports/complete-roster-native-verification.txt').write_text('\n'.join(lines)+'\n')
live=Path('reports/training-roster-live-verification.log').read_text()
assert 'PASS FBNeo haohmaru events=34 handler=25314' in live
assert live.count('PASS native character switch P')==34
assert live.count('PASS training preview/restore P')==34
print('PASS full roster: 17 native finish checks and 34 actual FBNeo training switches/previews/restores.')
