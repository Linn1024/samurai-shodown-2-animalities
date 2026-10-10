from pathlib import Path
import subprocess
import sys
ids=[0,1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17]
if len(sys.argv)>1: ids=[int(value,0) for value in sys.argv[1:]]
results=[]
for char in ids:
    Path('reports/test-target.txt').write_text(str(char))
    cmd=['tools/HBMAME/hbmame.exe','samsho2s29','-rompath','tools/HBMAME/roms','-video','none','-sound','none','-nothrottle','-seconds_to_run','51','-skip_gameinfo','-autoboot_script','reports/test-ultimate.lua','-nvram_directory','reports/test-nvram','-cfg_directory','reports/test-cfg']
    run=subprocess.run(cmd,capture_output=True,text=True)
    Path(f'reports/ultimate-{char:02x}.log').write_text(run.stdout+run.stderr)
    result=[line for line in run.stdout.splitlines() if line.startswith(('READY','RESULT','ULTIMATE ERROR'))]
    text=f'{char:02x}: '+ ' | '.join(result)
    print(text,flush=True)
    results.append(text)
Path('reports/ultimate-shadow-regression.txt' if len(sys.argv)>1 else 'reports/ultimate-results.txt').write_text('\n'.join(results))
