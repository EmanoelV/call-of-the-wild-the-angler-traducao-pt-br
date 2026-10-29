"""Registra aberturas/leituras de arquivos numa pasta (inotify). Uso: watch_open.py pasta segundos"""
import ctypes, os, struct, sys, time, select
libc = ctypes.CDLL('libc.so.6', use_errno=True)
fd = libc.inotify_init1(os.O_NONBLOCK)
IN_ACCESS, IN_OPEN = 0x1, 0x20
wds = {}
for root, dirs, files in os.walk(sys.argv[1]):
    wds[libc.inotify_add_watch(fd, root.encode(), IN_ACCESS | IN_OPEN)] = root
end = time.time() + float(sys.argv[2]); seen = set()
while time.time() < end:
    r, _, _ = select.select([fd], [], [], 1)
    if not r: continue
    buf = os.read(fd, 65536); i = 0
    while i < len(buf):
        wd, mask, cookie, ln = struct.unpack_from('iIII', buf, i)
        name = buf[i + 16:i + 16 + ln].rstrip(b'\0').decode()
        key = (wds.get(wd), name, 'OPEN' if mask & IN_OPEN else 'ACCESS')
        if key not in seen:
            seen.add(key); print(time.strftime('%H:%M:%S'), *key, flush=True)
        i += 16 + ln
print('fim', flush=True)
