#!/usr/bin/env python3
"""Mod de tradução PT-BR (extra-oficial) para Call of the Wild: The Angler.

A versão de varejo do jogo (motor Apex) não carrega arquivos soltos: a montagem
do "dropzone" foi compilada como função vazia e --vfs-fs não tem prioridade sobre
os .arc. Por isso o mod é aplicado no próprio arquivo, de forma reversível:
o text/master_eng.stringlookup traduzido é anexado ao FIM do game0.arc (os dados
originais não são tocados) e só a entrada correspondente no game0.tab passa a
apontar para ele. Antes disso são guardados um backup do .tab e o tamanho original
do .arc, usados pelo uninstall.

Uso (feche o jogo antes de install/uninstall):
  angler_l10n.py export    # gera translations/en.json (textos originais)
  angler_l10n.py build     # gera build/text/master_eng.stringlookup
  angler_l10n.py install   # build + aplica no game0.tab/.arc
  angler_l10n.py uninstall # restaura o .tab e o tamanho original do .arc
  angler_l10n.py status    # progresso da tradução
"""
import argparse, glob, hashlib, json, os, shutil, struct, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import apex, adf  # noqa: E402

__version__ = '1.0.0'
GAME_DIR_NAME = 'Call of the Wild The Angler'
TESTED_BUILD = '16541670'           # build Steam testado (AppVersion 2886386)


def steam_libraries():
    """Pastas steamapps conhecidas (Linux/Steam Deck/Windows), incluindo bibliotecas extras."""
    roots = [os.path.expanduser(p) for p in ('~/.steam/steam', '~/.local/share/Steam',
                                              '~/.var/app/com.valvesoftware.Steam/.local/share/Steam')]
    roots += [os.path.join(os.environ.get(v, ''), 'Steam') for v in ('ProgramFiles(x86)', 'ProgramFiles')]
    libs = []
    for r in roots:
        vdf = os.path.join(r, 'steamapps', 'libraryfolders.vdf')
        if os.path.exists(vdf):
            for line in open(vdf, encoding='utf-8', errors='replace'):
                if '"path"' in line:
                    libs.append(os.path.join(line.split('"')[3].replace('\\\\', '\\'), 'steamapps'))
        libs.append(os.path.join(r, 'steamapps'))
    seen, out = set(), []
    for l in libs:
        k = os.path.realpath(l)
        if k not in seen and os.path.isdir(l):
            seen.add(k); out.append(l)
    return out


def default_game():
    for lib in steam_libraries():
        g = os.path.join(lib, 'common', GAME_DIR_NAME)
        if os.path.isdir(os.path.join(g, 'archives_win64')):
            return g
    return None


TARGET = 'text/master_eng.stringlookup'
ENG_TAB_HASH = 0x8453ee3581f31f39   # hash do TARGET na tabela .tab (descoberto por varredura)
TRANS_DIR = os.path.join(MOD, 'translations')
CHUNK_DIR = os.path.join(TRANS_DIR, 'pt-BR')
SKIP_PREFIXES = ('eula_',)          # textos legais ficam no original
BACKUP = '.ptbr-orig'               # sufixo do backup da .tab
SIZEFILE = '.ptbr-size'             # sufixo do arquivo com o tamanho original do .arc


def installed_build(game):
    """buildid da Steam lido do appmanifest, se existir."""
    m = os.path.join(os.path.dirname(os.path.dirname(game)), 'appmanifest_1408610.acf')
    if os.path.exists(m):
        for line in open(m, encoding='utf-8', errors='replace'):
            if '"buildid"' in line:
                return line.split('"')[3]
    return None


def find_english(game):
    root = os.path.join(game, 'archives_win64', 'initial')
    allh, _ = apex.load_all(root, BACKUP)  # sempre lê a versão original
    if ENG_TAB_HASH in allh:
        e, _ = allh[ENG_TAB_HASH]
        data = apex.read_entry(e)
        if b'StringLookup' in data[:256] and b'gui_emote_2_name' in data:
            return data
    # fallback: varre por um StringLookup cujo texto seja inglês
    for h, (e, _) in allh.items():
        with open(e.archive, 'rb') as f:
            f.seek(e.offset); head = f.read(min(e.csize, 4096))
        if e.ctype == 1:
            head = zlib.decompressobj().decompress(head, 256)
        if head[:4] != b' FDA' or b'StringLookup.adf' not in head:
            continue
        data = apex.read_entry(e)
        s = adf.StringLookup(data)
        if any(s.cstr(n) == 'gui_emote_2_name' and s.cstr(t) == 'Thanks' for _, t, n in s.pairs):
            print(f'aviso: inglês encontrado em hash {h:016x} (atualize ENG_TAB_HASH)')
            return data
    sys.exit('erro: não encontrei o arquivo de textos em inglês')


def load_translations():
    tr = {}
    for fn in sorted(glob.glob(os.path.join(CHUNK_DIR, '*.json'))):
        with open(fn, encoding='utf-8') as f:
            for k, v in json.load(f).items():
                if isinstance(v, str) and v.strip():
                    tr[k] = v
    return tr


def english_pairs(data):
    s = adf.StringLookup(data)
    return s, {s.cstr(n): s.cstr(t) for _, t, n in s.pairs}


def cmd_export(a):
    data = find_english(a.game)
    _, en = english_pairs(data)
    os.makedirs(TRANS_DIR, exist_ok=True)
    with open(os.path.join(TRANS_DIR, 'en.json'), 'w', encoding='utf-8') as f:
        json.dump(dict(sorted(en.items())), f, ensure_ascii=False, indent=1)
    print(f'{len(en)} textos exportados para translations/en.json')


def rebuild(data, translations):
    """Refaz o blob Text na MESMA ordem do original, trocando cada texto pela tradução.

    O jogo depende do layout do Text: reordenar as strings (mesmo sem traduzir nada)
    faz o carregamento falhar, enquanto editar no lugar funciona. Por isso as strings
    são reescritas na ordem original (cada texto continua seguido do nome da sua
    chave) e só os offsets são deslocados. Os campos que apontam para o Text são:
    pares (TextOffset, NameOffset) e falas (NameOffset, PackageOffset).
    """
    s = adf.StringLookup(data)
    a = s.adf
    base, size = s.base, s.inst_size
    to, tflags, tc = s.arr_text
    assert to + tc == size, 'Text não é o último bloco da instância'
    inst = bytearray(data[base:base + size])
    keyed_en = {s.cstr(n): s.cstr(t) for _, t, n in s.pairs}
    by_en = {}
    for k, v in translations.items():
        if k in keyed_en:
            by_en.setdefault(keyed_en[k], v)
    # tradução escolhida para cada offset de texto (textos compartilhados usam a primeira)
    repl, changed = {}, 0
    for h, t, n in s.pairs:
        key, en = s.cstr(n), s.cstr(t)
        if key.startswith(SKIP_PREFIXES):
            continue
        pt = translations.get(key) or by_en.get(en)
        if pt and pt != en:
            repl.setdefault(t, pt.encode('utf-8'))
            changed += 1
    # reescreve as strings na ordem original e mapeia offset antigo -> novo
    text, remap, o = bytearray(), {}, 0
    while o < len(s.text):
        e = s.text.index(b'\0', o)
        remap[o] = len(text)
        text += repl.get(o, s.text[o:e]) + b'\0'
        o = e + 1
    po = s.arr_pairs[0]
    for i, (h, t, n) in enumerate(s.pairs):
        struct.pack_into('<III', inst, po + i * 12, h, remap[t], remap[n])
    for d in s.dialogue:
        struct.pack_into('<II', inst, d['o'] - base + 4, remap[d['name']], remap[d['pkg']])
    inst = inst[:to] + text
    struct.pack_into('<IIQ', inst, 32, to, tflags, len(text))
    new_size = len(inst)
    # remonta o arquivo: cabeçalho+comentário, instância, padding, tabelas finais
    head = bytearray(data[:base])
    pad = (-(base + new_size)) % 16
    delta = base + new_size + pad - a.oinst
    tail = bytearray(data[a.oinst:])
    struct.pack_into('<I', tail, 12, new_size)   # tamanho da instância 0 (tabela de instâncias)
    orig_pad = data[base + size:a.oinst]          # o padding original não é só zeros
    out = head + bytes(inst) + (orig_pad + b'\0' * 16)[:pad] + tail
    struct.pack_into('<4s10I', out, 0, b' FDA', 4, a.ninst, a.oinst + delta, a.ntype, a.otype + delta,
                     a.nhash, a.ohash + delta, a.nname, a.oname + delta, len(out))
    return bytes(out), changed, len(s.pairs)


def cmd_build(a):
    data = find_english(a.game)
    tr = load_translations()
    out, changed, total = rebuild(data, tr)
    # verificação: o resultado precisa ser lido de volta com as mesmas chaves
    s2 = adf.StringLookup(out)
    s1 = adf.StringLookup(data)
    assert [p[0] for p in s1.pairs] == [p[0] for p in s2.pairs]
    for (_, _, n1), (_, _, n2) in zip(s1.pairs, s2.pairs):
        assert s1.cstr(n1) == s2.cstr(n2)
    for d1, d2 in zip(s1.dialogue, s2.dialogue):
        assert (s1.cstr(d1['name']), s1.cstr(d1['pkg'])) == (s2.cstr(d2['name']), s2.cstr(d2['pkg']))
        assert d1['subs'] == d2['subs'] and d1['hash'] == d2['hash']

    dst = os.path.join(MOD, 'build', TARGET)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, 'wb') as f:
        f.write(out)
    print(f'{changed}/{total} textos substituídos -> build/{TARGET} ({len(out)} bytes)')
    return dst


def game_running():
    if os.name == 'nt':
        import subprocess
        out = subprocess.run(['tasklist'], capture_output=True, text=True).stdout
        return 'CotWTheAngler_Steam.exe' in out
    if not os.path.isdir('/proc'):
        return False
    for p in os.listdir('/proc'):
        try:
            argv = open(f'/proc/{p}/cmdline', 'rb').read().split(b'\0')
        except OSError:
            continue
        if any(x.endswith(b'CotWTheAngler_Steam.exe') for x in argv) and not argv[0].endswith((b'sh', b'bash')):
            return True
    return False


def locate_entry(game):
    """Acha (tab, índice) da entrada do master_eng, usando o .tab original."""
    root = os.path.join(game, 'archives_win64', 'initial')
    for t in sorted(glob.glob(os.path.join(root, '*.tab'))):
        src = t + BACKUP if os.path.exists(t + BACKUP) else t
        tab = apex.read_tab(t, open(src, 'rb').read())
        for i, e in enumerate(tab['entries']):
            if e.hash == ENG_TAB_HASH:
                return t, i
    sys.exit('erro: entrada do master_eng não encontrada nas .tab')


def restore(game):
    """Desfaz o patch (se houver). Retorna True se havia algo aplicado."""
    tabp, _ = locate_entry(game)
    arcp = tabp[:-4] + '.arc'
    if not os.path.exists(tabp + BACKUP):
        return False
    with open(tabp + SIZEFILE) as f:
        size, patched_sha = f.read().split()
        size = int(size)
    if hashlib.sha256(open(tabp, 'rb').read()).hexdigest() != patched_sha:
        # a Steam substituiu a .tab (atualização/verificação): o patch já não existe
        os.remove(tabp + BACKUP); os.remove(tabp + SIZEFILE)
        return False
    if os.path.getsize(arcp) < size:
        sys.exit(f'erro: {arcp} menor que o tamanho original salvo; o jogo foi atualizado? '
                 'Verifique a integridade dos arquivos na Steam e apague os arquivos *.ptbr-*')
    os.truncate(arcp, size)
    shutil.copyfile(tabp + BACKUP, tabp)
    os.remove(tabp + BACKUP); os.remove(tabp + SIZEFILE)
    return True


def cmd_install(a):
    if game_running():
        sys.exit('feche o jogo antes de instalar')
    src = cmd_build(a)
    data = open(src, 'rb').read()
    restore(a.game)
    tabp, idx = locate_entry(a.game)
    arcp = tabp[:-4] + '.arc'
    tabd = bytearray(open(tabp, 'rb').read())
    tab = apex.read_tab(tabp, bytes(tabd))
    size = os.path.getsize(arcp)
    shutil.copyfile(tabp, tabp + BACKUP)
    off = size + (-size) % tab['align']
    with open(arcp, 'r+b') as f:
        f.seek(size); f.write(b'\0' * (off - size)); f.write(data)
    # entrada: hash u64, offset u32, csize u32, usize u32, bloco u16, tipo u8 (0 = sem compressão), flags u8
    eo = tab['eoff'] + idx * 24
    struct.pack_into('<QIIIHBB', tabd, eo, ENG_TAB_HASH, off, len(data), len(data), 0, 0, 0)
    with open(tabp, 'wb') as f:
        f.write(tabd)
    with open(tabp + SIZEFILE, 'w') as f:
        f.write(f'{size} {hashlib.sha256(bytes(tabd)).hexdigest()}')
    # confere lendo de volta pelo caminho normal
    e = apex.read_tab(tabp)['entries'][idx]; e.archive = arcp
    assert apex.read_entry(e) == data
    print(f'instalado: {os.path.basename(tabp)} entrada {idx} -> {os.path.basename(arcp)} @ {off:#x}')
    print('No jogo, deixe o idioma do texto em English (aparece como "Português (BR)").')
    print('Após atualização do jogo ou "verificar integridade" na Steam, rode install de novo.')


def cmd_uninstall(a):
    if game_running():
        sys.exit('feche o jogo antes de desinstalar')
    print('mod removido, arquivos originais restaurados' if restore(a.game) else 'nada instalado')


def cmd_status(a):
    en_path = os.path.join(TRANS_DIR, 'en.json')
    if os.path.exists(en_path):
        with open(en_path, encoding='utf-8') as f:
            en = json.load(f)
    else:
        _, en = english_pairs(find_english(a.game))
    tr = load_translations()
    keys = [k for k in en if not k.startswith(SKIP_PREFIXES)]
    done = [k for k in keys if k in tr]
    ch = sum(len(en[k]) for k in done); tot = sum(len(en[k]) for k in keys)
    print(f'{len(done)}/{len(keys)} chaves traduzidas ({100*ch/max(tot,1):.1f}% do texto)')


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('cmd', choices=['export', 'build', 'install', 'uninstall', 'status'])
    p.add_argument('--game', help='pasta do jogo (padrão: detectada nas bibliotecas da Steam)')
    p.add_argument('--version', action='version', version=f'%(prog)s {__version__} (testado no build Steam {TESTED_BUILD})')
    a = p.parse_args()
    a.game = a.game or default_game()
    if not a.game or not os.path.isdir(os.path.join(a.game, 'archives_win64')):
        sys.exit('erro: pasta do jogo não encontrada; use --game "/caminho/para/Call of the Wild The Angler"')
    if a.cmd in ('install', 'uninstall'):
        build = installed_build(a.game)
        if build and build != TESTED_BUILD:
            print(f'aviso: build do jogo {build} diferente do testado ({TESTED_BUILD})')
    globals()['cmd_' + a.cmd](a)


if __name__ == '__main__':
    main()
