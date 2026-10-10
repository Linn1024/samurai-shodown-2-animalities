from pathlib import Path
import struct
results=[]
for frame in range(2600,2606):
    data=Path(f'reports/shadow-vram-{frame}.bin').read_bytes()
    v=struct.unpack(f'<{len(data)//2}H',data)
    size=0; shadow_tiles=[]
    for bank in range(0x17d):
        attr=v[0x8200+bank]
        if not attr&0x40: size=attr&0x3f
        for row in range(min(size,32)):
            tile=v[bank*64+row*2]
            flags=v[bank*64+row*2+1]
            tile|=(flags&0x70)<<12
            if 0x16e3e<=tile<=0x16e4b: shadow_tiles.append(tile)
    assert shadow_tiles,f'Frame {frame}: no shadows'
    results.append(f'Frame {frame}: {len(shadow_tiles)} visible shadow tiles, IDs '+','.join(hex(t) for t in sorted(set(shadow_tiles))))
Path('reports/steady-shadow-verification.txt').write_text('\n'.join(results)+'\nPASS: shadows stay drawn on every captured frame.\n')
print('\n'.join(results))
