from pathlib import Path
import sys
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image

out=Path('assets/ukyo-animality')
out.mkdir(parents=True,exist_ok=True)
for frame,name in [(2510,'native-idle'),(2740,'native-kneel')]:
    im=Image.open(f'reports/native-ukyo-{frame}.png').convert('RGBA')
    # Emulator capture isolates P1 palettes; remove the exact replacement backdrop.
    backdrop=im.getpixel((0,80))[:3]
    im.putdata([(0,0,0,0) if (r,g,b)==backdrop else (r,g,b,a) for r,g,b,a in im.get_flattened_data()])
    im=im.crop((50,90,185,224))
    im=im.crop(im.getbbox())
    im.save(out/(name+'.png'))
    im.resize((im.width*6,im.height*6),Image.Resampling.NEAREST).save(out/(name+'-reference.png'))
    print(name,im.size,backdrop)
