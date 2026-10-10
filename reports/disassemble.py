import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/capstone').resolve()))
from capstone import *
md=Cs(CS_ARCH_M68K,CS_MODE_BIG_ENDIAN|CS_MODE_M68K_000)
md.skipdata=True
for filename,address in [('063sp5.p1',0),('063sp.p2',0x100000),('063sp5.p3',0x200000)]:
    data=bytearray(Path('work/hack',filename).read_bytes())
    data[0::2],data[1::2]=data[1::2],data[0::2]
    out=Path('reports',filename+'.asm')
    out.write_text('\n'.join(f'{i.address:06x}: {i.mnemonic} {i.op_str}' for i in md.disasm(bytes(data),address)))
