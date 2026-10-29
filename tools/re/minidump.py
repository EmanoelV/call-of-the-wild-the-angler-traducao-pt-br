"""Lê a exceção de um minidump do Windows e mapeia o endereço para o módulo. Uso: minidump.py arquivo.dmp"""
import sys, struct
d = open(sys.argv[1], 'rb').read()
sig, ver, nstreams, rva = struct.unpack_from('<4sIII', d, 0)
streams = {}
for i in range(nstreams):
    t, size, r = struct.unpack_from('<III', d, rva + i * 12)
    streams[t] = (r, size)
def ustr(r):
    n = struct.unpack_from('<I', d, r)[0]
    return d[r + 4:r + 4 + n].decode('utf-16le')
mods = []
if 4 in streams:
    r, _ = streams[4]; n = struct.unpack_from('<I', d, r)[0]
    for i in range(n):
        o = r + 4 + i * 108
        base, size = struct.unpack_from('<QI', d, o); nrva = struct.unpack_from('<I', d, o + 20)[0]
        mods.append((base, size, ustr(nrva)))
def mod_of(a):
    for b, s, n in mods:
        if b <= a < b + s: return f'{n.split(chr(92))[-1]}+{a - b:#x}'
    return '?'
if 6 in streams:
    r, _ = streams[6]
    tid = struct.unpack_from('<I', d, r)[0]
    code, flags, rec, addr, nparams = struct.unpack_from('<IIQQI', d, r + 8)
    params = struct.unpack_from('<15Q', d, r + 8 + 32)[:nparams]
    print(f'thread {tid} exceção {code:#010x} em {addr:#x} ({mod_of(addr)}) params {[hex(p) for p in params]}')
    ctx_size, ctx_rva = struct.unpack_from('<II', d, r + 8 + 152)
    c = d[ctx_rva:ctx_rva + ctx_size]
    regs = ['rax','rcx','rdx','rbx','rsp','rbp','rsi','rdi','r8','r9','r10','r11','r12','r13','r14','r15','rip']
    vals = struct.unpack_from('<17Q', c, 0x78)
    print(' '.join(f'{n}={v:#x}' for n, v in zip(regs, vals)))
    rsp = vals[4]
    # pilha: procura endereços de retorno dentro de módulos na memória capturada
    mem = []
    if 9 in streams:  # Memory64List
        r9, _ = streams[9]; n, baserva = struct.unpack_from('<QQ', d, r9)
        cur = baserva
        for i in range(n):
            st, sz = struct.unpack_from('<QQ', d, r9 + 16 + i * 16); mem.append((st, sz, cur)); cur += sz
    if 5 in streams:
        r5, _ = streams[5]; n = struct.unpack_from('<I', d, r5)[0]
        for i in range(n):
            st, sz, mr = struct.unpack_from('<QII', d, r5 + 4 + i * 16); mem.append((st, sz, mr))
    for st, sz, mr in mem:
        if st <= rsp < st + sz:
            o = mr + (rsp - st)
            frames = []
            for k in range(0, min(0x2000, st + sz - rsp), 8):
                v = struct.unpack_from('<Q', d, o + k)[0]
                m = mod_of(v)
                if m != '?' and 'CotW' in m: frames.append(m)
            print('pilha (candidatos):', frames[:25]); break
