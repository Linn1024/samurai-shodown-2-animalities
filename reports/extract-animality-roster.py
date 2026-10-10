from pathlib import Path
import sys,json
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image,ImageDraw
roster=[(0,'haohmaru','Haohmaru','Tiger'),(1,'nakoruru','Nakoruru','Hawk'),(2,'hanzo','Hanzo Hattori','Snake'),(3,'galford','Galford','Wolf'),(4,'wan-fu','Wan-Fu','Elephant'),(5,'ukyo','Ukyo Tachibana','Swan'),(6,'kyoshiro','Kyoshiro Senryo','Fox'),(7,'gen-an','Gen-an Shiranui','Bat'),(8,'earthquake','Earthquake','Boar'),(9,'jubei','Jubei Yagyu','Turtle'),(11,'charlotte','Charlotte','Peacock'),(12,'genjuro','Genjuro Kibagami','Leopard'),(13,'cham-cham','Cham Cham','Monkey'),(14,'sieger','Neinhalt Sieger','Rhinoceros'),(15,'nicotine','Nicotine Caffeine','Owl'),(16,'mizuki','Mizuki Rashojin','Spider'),(17,'kuroko','Kuroko','Raven')]
root=Path('assets/native-roster');root.mkdir(exist_ok=True)
manifest=[]
atlas=Image.new('RGBA',(5*160,4*160),(32,40,56,255));draw=ImageDraw.Draw(atlas)
for n,(ident,slug,name,animal) in enumerate(roster):
    im=Image.open(f'reports/native-{slug}-roster-45.png').convert('RGBA')
    bg=im.getpixel((0,0))[:3]
    im.putdata([(0,0,0,0) if p[:3]==bg else p for p in im.get_flattened_data()])
    bbox=im.getbbox();im=im.crop(bbox);im.save(root/f'{slug}.png')
    im.resize((im.width*6,im.height*6),Image.Resampling.NEAREST).save(root/f'{slug}-reference.png')
    palette=int(Path(f'reports/native-{slug}-palette.txt').read_text(),16)
    ax,ay,compression=map(int,Path(f'reports/native-{slug}-anchor.txt').read_text().split())
    manifest.append({'id':ident,'slug':slug,'name':name,'animal':animal,'palette':palette,'reference_size':list(im.size),'anchor':[ax-bbox[0],ay-bbox[1]],'compression':compression})
    x=(n%5)*160;y=(n//5)*160
    draw.text((x+4,y+4),name,fill='white');atlas.alpha_composite(im,(x+(160-im.width)//2,y+155-im.height))
(root/'roster.json').write_text(json.dumps(manifest,indent=2))
atlas.save(root/'roster-reference.png')
print('Extracted all 17 native sprites and palette references.')
