import runpy,ctypes,time
from pathlib import Path
n=runpy.run_path('fbneo-ultimate.py'); u=n['u']; w=n['w']
pid=int(Path('reports/fbneo-probe-pid.txt').read_text())
def owned(h):
    p=w.DWORD(); u.GetWindowThreadProcessId(h,ctypes.byref(p)); return p.value==pid
main=next(h for h in n['windows']() if owned(h) and n['title'](h).startswith('FinalBurn'))
ctypes.set_last_error(0)
print('OPEN',u.PostMessageW(main,0x111,11812,0),ctypes.get_last_error())
time.sleep(1)
dlg=next(h for h in n['windows']() if owned(h) and u.GetDlgItem(h,20368))
print('SET',u.SetDlgItemTextA(dlg,20368,str(Path('ultimate.lua').resolve()).encode('mbcs')),ctypes.get_last_error())
print('TEXT',repr(n['control_text'](dlg,20368)))
ctypes.set_last_error(0)
print('RUN',u.PostMessageW(dlg,0x111,20366,u.GetDlgItem(dlg,20366)),ctypes.get_last_error())
time.sleep(2)
print('OUT',repr(n['control_text'](dlg,20369)))
print('WINDOWS',[(h,ascii(n['title'](h))) for h in n['windows']() if owned(h)])
