"""Leitor/extrator para arquivos TAB v3 / ARC do motor Apex (The Angler)."""
import struct, zlib, os, glob

def _rot(x, k): return ((x << k) | (x >> (32 - k))) & 0xffffffff

def hashlittle2(data: bytes, pc=0, pb=0):
    """Bob Jenkins lookup3 hashlittle2 -> (c, b)."""
    length = len(data)
    a = b = c = (0xdeadbeef + length + pc) & 0xffffffff
    c = (c + pb) & 0xffffffff
    i = 0
    M = 0xffffffff
    while length > 12:
        a = (a + struct.unpack_from('<I', data, i)[0]) & M
        b = (b + struct.unpack_from('<I', data, i + 4)[0]) & M
        c = (c + struct.unpack_from('<I', data, i + 8)[0]) & M
        a = (a - c) & M; a ^= _rot(c, 4);  c = (c + b) & M
        b = (b - a) & M; b ^= _rot(a, 6);  a = (a + c) & M
        c = (c - b) & M; c ^= _rot(b, 8);  b = (b + a) & M
        a = (a - c) & M; a ^= _rot(c, 16); c = (c + b) & M
        b = (b - a) & M; b ^= _rot(a, 19); a = (a + c) & M
        c = (c - b) & M; c ^= _rot(b, 4);  b = (b + a) & M
        length -= 12; i += 12
    if length == 0:
        return c, b
    tail = data[i:] + b'\0' * (12 - length)
    a = (a + struct.unpack_from('<I', tail, 0)[0]) & M
    b = (b + struct.unpack_from('<I', tail, 4)[0]) & M
    c = (c + struct.unpack_from('<I', tail, 8)[0]) & M
    c ^= b; c = (c - _rot(b, 14)) & M
    a ^= c; a = (a - _rot(c, 11)) & M
    b ^= a; b = (b - _rot(a, 25)) & M
    c ^= b; c = (c - _rot(b, 16)) & M
    a ^= c; a = (a - _rot(c, 4)) & M
    b ^= a; b = (b - _rot(a, 14)) & M
    c ^= b; c = (c - _rot(b, 24)) & M
    return c, b

def hash64(name: str) -> int:
    c, b = hashlittle2(name.encode())
    return c | (b << 32)

def hash32(name: str) -> int:
    return hashlittle2(name.encode())[0]

class Entry:
    __slots__ = ('hash', 'offset', 'csize', 'usize', 'block', 'ctype', 'flags', 'archive')

def read_tab(path, data=None):
    d = data if data is not None else open(path, 'rb').read()
    magic, ver, endian, align, nentries, nblocks = struct.unpack_from('<4sHHIII', d, 0)
    assert magic == b'TAB\0' and ver == 3, (magic, ver)
    # tabela de blocos: (tamanho comprimido, tamanho descomprimido) iniciando em 0x18
    boff = 0x18
    eoff = len(d) - nentries * 24
    nb = (eoff - boff) // 8
    blocks = [struct.unpack_from('<II', d, boff + i * 8) for i in range(nb)]
    entries = []
    for i in range(nentries):
        e = Entry()
        e.hash, e.offset, e.csize, e.usize, e.block, e.ctype, e.flags = struct.unpack_from('<QIIIHBB', d, eoff + i * 24)
        e.archive = path[:-4] + '.arc'
        entries.append(e)
    return dict(align=align, blocks=blocks, entries=entries, eoff=eoff)

def load_all(root, backup_suffix=None):
    """Carrega todas as .tab; se existir <tab><backup_suffix>, usa o backup (original)."""
    out = {}
    tabs = {}
    for t in sorted(glob.glob(os.path.join(root, '*.tab'))):
        b = t + backup_suffix if backup_suffix else None
        tab = read_tab(t, open(b, 'rb').read() if b and os.path.exists(b) else None)
        tabs[t] = tab
        for e in tab['entries']:
            out.setdefault(e.hash, (e, tab))
    return out, tabs

def read_entry(e, f=None):
    own = f is None
    if own: f = open(e.archive, 'rb')
    f.seek(e.offset)
    raw = f.read(e.csize)
    if own: f.close()
    if e.ctype == 0:
        return raw
    out = bytearray()
    buf = raw
    while len(out) < e.usize and buf:
        # pula padding entre blocos zlib
        i = 0
        while i < len(buf) and buf[i] != 0x78: i += 1
        buf = buf[i:]
        d = zlib.decompressobj()
        out += d.decompress(buf)
        buf = d.unused_data
    return bytes(out)
