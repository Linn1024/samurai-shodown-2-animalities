from pathlib import Path
import sys,json,shutil
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image,ImageDraw

root=Path('assets/galford-animality')
stage=Path('reports/galford-cleanup-candidate');stage.mkdir(exist_ok=True)
generated=Path('C:/Users/linn1/.codex/generated_images/01a12259-5416-7c60-8115-a389a45534d0/exec-fe571754-e4fb-4994-a253-f4b1fccd0576.png')
im=Image.open(generated).convert('RGBA')
assert im.size==(1448,1086),im.size
shutil.copy2(generated,stage/'source-v4.generated.png')
im.resize((724,543),Image.Resampling.NEAREST).save(stage/'source-v4.png')
cfg=json.loads((root/'build-config.json').read_text());cfg['source_file']='source-v4.png'
(stage/'build-config.json').write_text(json.dumps(cfg,indent=2)+'\n')
print('Prepared 724x543 source at 1:1 game scale, with exact 2:1 reduction of generated output.')
