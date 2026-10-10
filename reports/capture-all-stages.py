from pathlib import Path
import json,subprocess
root=Path('reports/stages');root.mkdir(exist_ok=True)
roster=json.loads(Path('assets/native-roster/roster.json').read_text())
command=[str(Path('tools/HBMAME/hbmame.exe').resolve()),'samsho2s29','-rompath','tools/HBMAME/roms','-pluginspath','tools/HBMAME/plugins','-nvram_directory','reports/test-nvram','-video','none','-sound','none','-nothrottle','-seconds_to_run','51','-console','-skip_gameinfo']
for r in roster:
 slug=r['slug']
 script=f"SS2_STAGE={r['id']}; SS2_STAGE_SLUG='{slug}'; dofile('reports/capture-stage-foreground.lua')\n"
 result=subprocess.run(command,input=script,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=40)
 (root/(slug+'.log')).write_text(result.stdout,encoding='utf-8')
 assert result.returncode==0 and result.stdout.count('STAGE CAPTURE ')==3,(slug,result.stdout[-1800:])
 print('Captured '+slug+' stage: left, center, right.',flush=True)
