"""Desmonta um intervalo de VA de um PE x64. Uso: disasm.py exe va_ini va_fim"""
import sys, struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
exe, a, b = sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)
data = open(exe, 'rb').read()
pe = struct.unpack_from('<I', data, 0x3c)[0]
nsec = struct.unpack_from('<H', data, pe + 6)[0]; optsz = struct.unpack_from('<H', data, pe + 20)[0]
base = struct.unpack_from('<Q', data, pe + 48)[0]
secs = []
for i in range(nsec):
    o = pe + 24 + optsz + i * 40
    vs, va, rs, rp = struct.unpack_from('<IIII', data, o + 8); secs.append((va, rs, rp))
def va2off(v):
    for va, rs, rp in secs:
        if base + va <= v < base + va + rs: return v - base - va + rp
def cstr(v):
    o = va2off(v)
    if o is None: return None
    e = data.find(b'\0', o, o + 120)
    s = data[o:e]
    return s.decode('latin1') if e > o and all(32 <= c < 127 for c in s) else None
md = Cs(CS_ARCH_X86, CS_MODE_64)
o = va2off(a)
for ins in md.disasm(data[o:o + (b - a)], a):
    note = ''
    if 'rip' in ins.op_str and '[rip' in ins.op_str:
        try:
            disp = int(ins.op_str.split('rip')[1].split(']')[0].replace(' ', ''), 16)
            t = ins.address + ins.size + disp; s = cstr(t); note = f'  ; {hex(t)}' + (f' "{s}"' if s else '')
        except Exception: pass
    print(f'{ins.address:x}: {ins.mnemonic} {ins.op_str}{note}')
