"""Teste: grava um stringlookup qualquer no fim do game0.arc e reaponta a entrada (patch já instalado)."""
import sys, struct, os, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')); import apex
I, src = sys.argv[1], sys.argv[2]
tabp = I + '/game0.tab'; arcp = I + '/game0.arc'
data = open(src, 'rb').read()
size = int(open(tabp + '.ptbr-size').read().split()[0])
os.truncate(arcp, size)
tabd = bytearray(open(tabp + '.ptbr-orig', 'rb').read()); tab = apex.read_tab(tabp, bytes(tabd))
off = size + (-size) % tab['align']
with open(arcp, 'r+b') as f:
    f.seek(size); f.write(b'\0' * (off - size)); f.write(data)
struct.pack_into('<QIIIHBB', tabd, tab['eoff'] + 2887 * 24, 0x8453ee3581f31f39, off, len(data), len(data), 0, 0, 0)
open(tabp, 'wb').write(tabd)
open(tabp + '.ptbr-size', 'w').write(f'{size} {hashlib.sha256(bytes(tabd)).hexdigest()}')
print('instalado', src, len(data), 'bytes @', hex(off))
