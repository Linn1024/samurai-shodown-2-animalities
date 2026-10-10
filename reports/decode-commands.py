from pathlib import Path
def swap(name):
    data=bytearray(Path('work/hack',name).read_bytes()); data[0::2],data[1::2]=data[1::2],data[0::2]; return data
rom=swap('063sp5.p1')+swap('063sp.p2')
extra=swap('063sp5.p3')
def read(address,size):
    if address>=0x900000: return extra[address-0x900000:address-0x900000+size]
    return rom[address:address+size]
def u32(address): return int.from_bytes(read(address,4),'big')
handlers=[int.from_bytes(extra[0x3346+i*4:0x334a+i*4],'big') for i in range(32)]
print('HANDLERS',','.join(f'{i}:{v:x}' for i,v in enumerate(handlers)))
for char in [0,1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17]:
    ptr=u32(0x6c9ea+char*4)
    print(f'CHAR {char:x} TABLE {ptr:x}')
    for i in range(32):
        row=read(ptr+i*8,8)
        if len(row)<8 or int.from_bytes(row[:4],'big')==0: break
        motion=int.from_bytes(row[:4],'big')
        handler=handlers[row[7]] if row[7]<len(handlers) else 0
        print(f' {i}: motion={motion:x} move={row[5]:x} weapon={row[6]:x} handler={handler:x} '+read(motion,40).hex())
