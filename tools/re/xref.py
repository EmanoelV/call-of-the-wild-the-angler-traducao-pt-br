"""Acha referências (lea rip-relative) a strings num PE x64. Uso: xref.py exe str1 str2..."""
import sys, struct, re, collections

exe = sys.argv[1]; targets = sys.argv[2:]
data = open(exe, 'rb').read()
pe = struct.unpack_from('<I', data, 0x3c)[0]
nsec = struct.unpack_from('<H', data, pe + 6)[0]
optsz = struct.unpack_from('<H', data, pe + 20)[0]
base = struct.unpack_from('<Q', data, pe + 24 + 24)[0]
secs = []
for i in range(nsec):
    o = pe + 24 + optsz + i * 40
    name = data[o:o + 8].rstrip(b'\0')
    vs, va, rs, rp = struct.unpack_from('<IIII', data, o + 8)
    secs.append((name, va, rs, rp))

def off2va(o):
    for n, va, rs, rp in secs:
        if rp <= o < rp + rs:
            return base + va + o - rp

n, va, rs, rp = [s for s in secs if s[0] == b'.text'][0]
tb = data[rp:rp + rs]; tva = base + va
idx = collections.defaultdict(list)
for mm in re.finditer(rb'[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]', tb):
    i = mm.start()
    idx[tva + i + 7 + struct.unpack_from('<i', tb, i + 3)[0]].append(tva + i)
for t in targets:
    for m in re.finditer(re.escape(t.encode()) + b'\0', data):
        if m.start() > 0 and data[m.start() - 1] != 0:
            continue
        v = off2va(m.start())
        print('STR', repr(t), hex(v), 'xrefs', [hex(x) for x in idx.get(v, [])], flush=True)
