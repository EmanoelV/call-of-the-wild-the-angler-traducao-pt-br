"""Parser mínimo do formato ADF v4 (Apex Data Format)."""
import struct

class ADF:
    def __init__(self, data: bytes):
        self.d = d = data
        (magic, ver, self.ninst, self.oinst, self.ntype, self.otype,
         self.nhash, self.ohash, self.nname, self.oname, self.total) = struct.unpack_from('<4s10I', d, 0)
        assert magic == b' FDA' and ver == 4
        # nametable: N bytes de comprimento + strings terminadas em \0
        lens = d[self.oname:self.oname + self.nname]
        p = self.oname + self.nname
        self.names = []
        for L in lens:
            self.names.append(d[p:p + L].decode())
            p += L + 1
        # string hashes: string\0 ... depois u64 hash por string (layout do deca)
        self.instances = []
        for i in range(self.ninst):
            nh, th, off, size, nidx = struct.unpack_from('<IIIIQ', d, self.oinst + i * 24)
            self.instances.append(dict(name_hash=nh, type_hash=th, offset=off, size=size, name=self.names[nidx]))
        self.types = {}
        p = self.otype
        for i in range(self.ntype):
            meta, size, align, th, nidx, flags, eth, elen = struct.unpack_from('<IIIIQIII', d, p)
            p += 36
            t = dict(meta=meta, size=size, align=align, hash=th, name=self.names[nidx], flags=flags,
                     elem=eth, elen=elen, members=[])
            cnt, = struct.unpack_from('<I', d, p); p += 4
            if meta == 1:      # struct
                for _ in range(cnt):
                    mn, mth, malign, moff, mdef_t, mdef = struct.unpack_from('<QIIIIQ', d, p)
                    p += 32
                    t['members'].append(dict(name=self.names[mn], type=mth, align=malign,
                                             offset=moff & 0xffffff, bit=moff >> 24))
            elif meta == 8:    # enum
                p += cnt * 12
            self.types[th] = t

class StringLookup:
    """Decodifica a instância 'stringlookup' (StringLookup)."""
    def __init__(self, data: bytes):
        self.adf = a = ADF(data)
        inst = a.instances[0]
        self.base = b = inst['offset']
        self.inst_size = inst['size']
        d = data
        def arr(o):
            off, flags, cnt = struct.unpack_from('<IIQ', d, b + o)
            return off, flags, cnt
        self.arr_pairs = arr(0); self.arr_dlg = arr(16); self.arr_text = arr(32)
        po, _, pc = self.arr_pairs
        self.pairs = [struct.unpack_from('<III', d, b + po + i * 12) for i in range(pc)]
        to, _, tc = self.arr_text
        self.text = d[b + to:b + to + tc]
        do, _, dc = self.arr_dlg
        self.dialogue = []
        for i in range(dc):
            o = b + do + i * 56
            h, name, pkg, snd, flags = struct.unpack_from('<IIIII', d, o)
            prop = struct.unpack_from('<IIQ', d, o + 24)
            subs = struct.unpack_from('<IIQ', d, o + 40)
            sl = [struct.unpack_from('<Iff', d, b + subs[0] + k * 12) for k in range(subs[2])]
            self.dialogue.append(dict(hash=h, name=name, pkg=pkg, snd=snd, flags=flags, prop=prop, subs=sl, o=o))

    def cstr(self, off):
        e = self.text.index(b'\0', off)
        return self.text[off:e].decode('utf-8')
