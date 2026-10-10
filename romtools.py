"""Local Samurai Shodown II workbench. Originals are read-only inputs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
HACK = {
    '063sp5.p1': ('063-p1sp.p1', '063s29.p1'),
    '063sp.p2': ('063-p2sp.sp2', '063s25.p2'),
    '063sp5.p3': ('063-p3sp.p3', '063s29.p3'),
    '063-s1sp.s1': ('063-s1sp.s1', '063s25.s1'),
    '063-c7sp.c7': ('063-c7sp.c7', '063s25.c7'),
    '063-c8sp.c8': ('063-c8sp.c8', '063s25.c8'),
}
REPLACED = {'063-p1.p1', '063-s1.s1', '063-c7.c7', '063-c8.c8'}

def prepare():
    for archive, destination in [('samsho2.zip', 'base'), ('samsho2sp.zip', 'hack'), ('samsho2sp.zip', 'baseline-hack')]:
        folder = ROOT / 'work' / destination
        folder.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(ROOT / archive) as z:
            for item in z.infolist():
                target = folder / Path(item.filename).name
                if not target.exists():
                    target.write_bytes(z.read(item))
    for file in (ROOT / 'work/base').iterdir():
        if file.name not in REPLACED:
            target = ROOT / 'work/hack' / file.name
            if not target.exists():
                shutil.copy2(file, target)
    print('Working files ready in work/base and work/hack. Existing edits retained.')

def build():
    folder = ROOT / 'work/hack'
    if not folder.exists():
        raise SystemExit('Run prepare first.')
    required = set(HACK)
    with zipfile.ZipFile(ROOT / 'samsho2.zip') as z:
        required.update(n for n in z.namelist() if n not in REPLACED)
    missing = sorted(n for n in required if not (folder / n).is_file())
    if missing:
        raise SystemExit('Missing working ROMs: ' + ', '.join(missing))
    manifest = []
    for index, (emulator, setname) in enumerate([('FBNeo', 'samsh2sp'), ('HBMAME', 'samsho2s29')]):
        roms = ROOT / 'tools' / emulator / 'roms'
        roms.mkdir(parents=True, exist_ok=True)
        destination = roms / (setname + '.zip')
        temp = destination.with_suffix('.tmp')
        with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as z:
            for file in sorted(folder.iterdir()):
                if file.name in HACK:
                    name = HACK[file.name][index]
                elif file.name in REPLACED or file.suffix.lower() not in {'.c1','.c2','.c3','.c4','.c5','.c6','.m1','.v1','.v2','.v3','.v4'}:
                    continue
                else:
                    name = file.name if index == 0 else file.name.replace('063-', '063.')
                z.write(file, name)
        temp.replace(destination)
        for original in ['samsho2.zip', 'neogeo.zip']:
            target = roms / original
            if not target.exists():
                shutil.copy2(ROOT / original, target)
        manifest.append({'file': str(destination.relative_to(ROOT)), 'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()})
        print('Built', destination)
    (ROOT / 'reports/build.json').write_text(json.dumps(manifest, indent=2))

def audit():
    result = {}
    for name in ['samsho2.zip','samsho2sp.zip','neogeo.zip']:
        with zipfile.ZipFile(ROOT / name) as z:
            bad = z.testzip()
            if bad:
                raise SystemExit(f'Corrupt entry: {bad}')
            result[name] = [{'name': e.filename, 'size': e.file_size, 'crc32': f'{e.CRC:08x}'} for e in z.infolist()]
    (ROOT / 'reports/rom-inventory.json').write_text(json.dumps(result, indent=2))
    print('All three original ZIP archives pass integrity checks.')

def ips(source, modified, output):
    old, new = Path(source).read_bytes(), Path(modified).read_bytes()
    if len(old) != len(new) or len(new) > 0xffffff:
        raise SystemExit('IPS export supports equal-sized ROM files up to 16 MiB.')
    patch = bytearray(b'PATCH')
    pos = 0
    while pos < len(new):
        if old[pos] == new[pos]:
            pos += 1
            continue
        start = pos
        if start == 0x454f46:  # Avoid reserved EOF record offset.
            start -= 1
        pos += 1
        while pos < len(new) and old[pos] != new[pos] and pos-start < 65535:
            pos += 1
        data = new[start:pos]
        patch += start.to_bytes(3,'big') + len(data).to_bytes(2,'big') + data
    patch += b'EOF'
    Path(output).write_bytes(patch)
    print('Exported', output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare','build','audit','ips'])
    parser.add_argument('files', nargs='*')
    args = parser.parse_args()
    if args.command == 'ips':
        if len(args.files) != 3:
            parser.error('ips requires ORIGINAL_FILE MODIFIED_FILE OUTPUT.ips')
        ips(*args.files)
    else:
        globals()[args.command]()
