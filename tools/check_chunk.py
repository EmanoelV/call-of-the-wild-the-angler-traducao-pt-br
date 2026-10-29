#!/usr/bin/env python3
"""Valida uma tradução de lote: python3 tools/check_chunk.py NNN"""
import json, os, re, sys
MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
n = sys.argv[1].zfill(3)
src = json.load(open(f'{MOD}/translations/chunks/{n}.json', encoding='utf-8'))
try:
    out = json.load(open(f'{MOD}/translations/pt-BR/c{n}.json', encoding='utf-8'))
except Exception as e:
    sys.exit(f'ERRO: JSON inválido ou ausente: {e}')
TOK = re.compile(r"\{[^}]*\}|</?(?:p|li|ul|ol|b|i|br|font)\b[^>]*>|\\n|\n")
errs = []
missing = [k for k in src if k not in out]
extra = [k for k in out if k not in src]
if missing: errs.append(f'chaves faltando ({len(missing)}): {missing[:10]}')
if extra: errs.append(f'chaves extras ({len(extra)}): {extra[:10]}')
for k, v in src.items():
    if k not in out: continue
    t = out[k]
    if not isinstance(t, str) or not t.strip():
        errs.append(f'{k}: valor vazio'); continue
    if sorted(TOK.findall(v)) != sorted(TOK.findall(t)):
        errs.append(f'{k}: marcadores diferentes. original={sorted(TOK.findall(v))} traducao={sorted(TOK.findall(t))}')
if errs:
    print('\n'.join(errs[:40])); print(f'{len(errs)} problema(s)'); sys.exit(1)
print(f'OK ({len(out)} chaves)')
