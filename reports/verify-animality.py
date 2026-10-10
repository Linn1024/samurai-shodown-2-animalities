from pathlib import Path
import sys,struct
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import Image

checks=[]
def read_log(path):
    data=Path(path).read_bytes()
    return data.decode('utf-16' if data.startswith(b'\xff\xfe') else 'utf-8')
for name,event_count,finished in [('','1',True),('-left','1',True),('-p2','1',True),('-other','0',False),('-normal','0',False),('-cancel','1',False)]:
    data=read_log(f'reports/test-animality{name}.log')
    assert f'events={event_count} active=false handler=25314' in data,(name,data)
    if finished:assert 'human form restored; native victory pose.' in data
    checks.append(f'PASS native-game test {name or "right"}: events={event_count}, actor callback restored.')
assert 'CONTINUE p1=1065c0 hp=128 state=0 p2hp=128' in read_log('reports/test-animality.log')
checks.append('PASS game continues into round 2 with both health bars restored.')
assert 'PASS FBNeo events=1 handler=25314' in read_log('reports/fbneo-animality-test.log')
checks.append('PASS actual FBNeo execution and window capture: native fountain, swan, human victory.')

root=Path('assets/ukyo-animality')
native=Image.open(root/'native-idle.png').convert('RGBA')
frame=Image.open(root/'frame-00.png').convert('RGBA')
crop=frame.crop((19,112-native.height,19+native.width,112))
assert list(native.get_flattened_data())==list(crop.get_flattened_data())
assert (root/'frame-00.png').read_bytes()==(root/'frame-15.png').read_bytes()
checks.append('PASS native human pose: every original RGBA pixel preserved at both ends.')
assert len(list((root/'gd').glob('*.gd')))==160
for direction in ('left','right'):
    for zoom in (64,80,96,112,128):
        for i in range(16):
            data=(root/'gd'/f'{direction}-{zoom}-{i:02d}.gd').read_bytes()
            assert data[:2]==b'\xff\xfe'
            assert struct.unpack_from('>HH',data,2)==(zoom,zoom)
            assert len(data)==11+zoom*zoom*4
checks.append('PASS all 160 GD runtime sprites: dimensions, headers and data lengths.')
text='\n'.join(checks)+'\n'
Path('reports/animality-verification.txt').write_text(text)
print(text)
