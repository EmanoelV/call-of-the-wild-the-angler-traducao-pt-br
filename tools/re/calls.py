"""Acha chamadas diretas (call rel32) para um VA. Uso: calls.py exe va"""
import sys, struct, re
exe, target = sys.argv[1], int(sys.argv[2], 16)
data = open(exe, 'rb').read()
pe = struct.unpack_from('<I', data, 0x3c)[0]; nsec = struct.unpack_from('<H', data, pe + 6)[0]
optsz = struct.unpack_from('<H', data, pe + 20)[0]; base = struct.unpack_from('<Q', data, pe + 48)[0]
for i in range(nsec):
    o = pe + 24 + optsz + i * 40
    if data[o:o + 5] != b'.text': continue
    vs, va, rs, rp = struct.unpack_from('<IIII', data, o + 8)
    tb = data[rp:rp + rs]
    for m in re.finditer(b'\xe8', tb):
        j = m.start()
        if base + va + j + 5 + struct.unpack_from('<i', tb, j + 1)[0] == target if j + 5 <= len(tb) else False:
            print(hex(base + va + j))
