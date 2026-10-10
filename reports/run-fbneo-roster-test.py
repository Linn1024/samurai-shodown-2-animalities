"""Launch and capture only the FBNeo instance owned by this test."""
import argparse,ctypes,subprocess,sys,time
from ctypes import wintypes as w
from pathlib import Path
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import ImageGrab,Image
parser=argparse.ArgumentParser();parser.add_argument('id',type=int);parser.add_argument('slug');parser.add_argument('--script',default='reports/fbneo-test-roster.lua');parser.add_argument('--stage',type=int);parser.add_argument('--expected-events',type=int,default=1);parser.add_argument('--capture-frames',type=int,default=90);parser.add_argument('--completion-timeout',type=int,default=0);args=parser.parse_args()
root=Path.cwd();marker=root/f'reports/fbneo-{args.slug}-started.txt'
if marker.exists():marker.unlink()
(root/'reports/fbneo-roster-config.txt').write_text(f'{args.id} {args.slug}'+(f' {args.stage}' if args.stage is not None else ''))
u=ctypes.WinDLL('user32')
u.GetWindowTextW.argtypes=[w.HWND,w.LPWSTR,ctypes.c_int]
u.PostMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM]
u.ShowWindow.argtypes=[w.HWND,ctypes.c_int]
CB=ctypes.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
startup=subprocess.STARTUPINFO();startup.dwFlags=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
folder=root/'reports/fbneo-shadow-test'
p=subprocess.Popen([str(folder/'fbneo64.exe'),str(root/args.script)],cwd=folder,startupinfo=startup)
main=[]
@CB
def find(h,_):
 pid=w.DWORD();u.GetWindowThreadProcessId(h,ctypes.byref(pid))
 name=ctypes.create_unicode_buffer(512);u.GetWindowTextW(h,name,len(name))
 if pid.value==p.pid and 'FinalBurn Neo' in name.value:main.append(h)
 return True
try:
 deadline=time.monotonic()+15
 while not main and time.monotonic()<deadline:
  u.EnumWindows(find,0);time.sleep(.1)
 assert main,'Owned FBNeo window not found'
 h=main[0];u.ShowWindow(h,5);u.PostMessageW(h,0x111,10617,0)
 deadline=time.monotonic()+45
 while not marker.exists() and time.monotonic()<deadline:
  if p.poll() is not None:raise RuntimeError('Test FBNeo exited before animation')
  time.sleep(.1)
 if not marker.exists():
  main.clear();u.EnumWindows(find,0)
  if main:ImageGrab.grab(window=main[0]).save(root/'reports/fbneo-fixture-failure.png')
 assert marker.exists(),'Animality did not start; inspect test log'
 # Loading the ROM can recreate FBNeo's video window; discard the startup HWND.
 main.clear();u.EnumWindows(find,0);assert main,'Loaded test window not found'
 h=main[0];u.ShowWindow(h,5)
 output=root/(f'assets/foreground/stage-{args.stage}' if args.stage is not None else f'assets/{args.slug}-animality');output.mkdir(exist_ok=True);frames=[]
 for i in range(args.capture_frames):
  im=ImageGrab.grab(window=h)
  if i in (8,45,58,80):im.save(output/f'fbneo-live-{i:02d}.png')
  frames.append(im.resize((640,492),Image.Resampling.NEAREST));time.sleep(.07)
 frames[0].save(output/'fbneo-live-finish.gif',save_all=True,append_images=frames[1:],duration=80,loop=0)
 log=(root/f'reports/fbneo-{args.slug}-test.log').read_text()
 deadline=time.monotonic()+args.completion_timeout
 while f'PASS FBNeo {args.slug} events={args.expected_events} handler=25314' not in log and time.monotonic()<deadline:
  if p.poll() is not None:break
  time.sleep(.2);log=(root/f'reports/fbneo-{args.slug}-test.log').read_text()
 if args.stage is not None:(root/f'reports/fbneo-stage-{args.stage}-test.log').write_text(log)
 assert f'PASS FBNeo {args.slug} events={args.expected_events} handler=25314' in log,log[-2000:]
 assert 'torso strike / native blood fountain.' in log and 'human form restored; native victory pose.' in log and 'timeout after' not in log,log[-2000:]
 print(f'PASS actual FBNeo {args.slug}: native fountain, animality, victory and owned-window GIF capture.')
finally:
 if main:u.PostMessageW(main[0],0x10,0,0)
 try:p.wait(timeout=8)
 except subprocess.TimeoutExpired:
  p.terminate();p.wait(timeout=5)
  print(f'Closed owned test process {p.pid}; no unrelated emulator was touched.')
