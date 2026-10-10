import runpy
import ctypes
ns=runpy.run_path('C:/TEMP2/SS2/fbneo-ultimate.py')
u,CB=ns['u'],ns['CALLBACK']
for h in ns['windows']():
    caption=ns['title'](h)
    if caption in ['Lua Script','Lua load error','Lua run error']:
        print('WINDOW',h,repr(caption),flush=True)
        @CB
        def child(handle,_):
            name=ctypes.create_unicode_buffer(256)
            u.GetClassNameW(handle,name,len(name))
            print(u.GetDlgCtrlID(handle),name.value,ascii(ns['title'](handle)),flush=True)
            return True
        u.EnumChildWindows(h,child,0)
