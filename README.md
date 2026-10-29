# Call of the Wild: The Angler — Tradução PT-BR (Português do Brasil)

![versão](https://img.shields.io/badge/vers%C3%A3o-1.0.0-blue)
![jogo](https://img.shields.io/badge/build%20Steam-16541670-informational)
![plataforma](https://img.shields.io/badge/testado-Linux%20%2F%20Proton-success)
![status](https://img.shields.io/badge/projeto-f%C3%A3%20%C2%B7%20n%C3%A3o%20oficial-orange)

**Tradução não oficial, feita por fã, de _Call of the Wild: The Angler_ para português do Brasil.**
Menus, opções, tutoriais, legendas dos diálogos, códex, diário, missões, desafios,
loja, equipamentos, iscas e nomes de peixes em PT-BR.

> 🇺🇸 **English summary:** unofficial Brazilian Portuguese (pt-BR) fan translation mod for
> *Call of the Wild: The Angler* (Steam). It patches the game's English text table in a
> reversible way (backup + one-command uninstall). No game files are redistributed: the
> installer reads your own copy of the game and applies the translation locally.
> See [English](#english) below.

---

## Versão e compatibilidade

| | |
|---|---|
| Versão do mod | **1.0.0** (veja o [CHANGELOG](CHANGELOG.md)) |
| Jogo | Call of the Wild: The Angler — Steam (app 1408610) |
| Build testado | Steam build **16541670** · AppVersion 2886386 |
| Testado em | Linux (Steam + Proton) |
| Windows / Steam Deck | deve funcionar (mesmos arquivos do jogo), mas ainda não foi testado |
| Cobertura | ~9.400 de 10.551 textos (98,7% do texto do jogo) |
| Não traduzido | termos legais (EULA), nomes próprios, marcas e modelos de equipamento |

Depois de uma **atualização do jogo** ou de **"Verificar integridade dos arquivos"** na
Steam, a tradução é desfeita pela própria Steam. Basta rodar o `install` de novo.

## Instalação

Requisito: **Python 3.8+**. No Linux e no Steam Deck ele normalmente já vem instalado.
No Windows, instale pelo [python.org](https://www.python.org/downloads/).

1. Baixe a [última versão](../../releases/latest) (ou `git clone` este repositório).
2. **Feche o jogo.**
3. Rode o instalador na pasta do mod:

   ```bash
   # Linux / Steam Deck (modo Desktop, Konsole)
   python3 tools/angler_l10n.py install
   ```
   ```bat
   :: Windows (Prompt de Comando)
   py tools\angler_l10n.py install
   ```

   A pasta do jogo é encontrada automaticamente nas bibliotecas da Steam. Se não for,
   informe-a com `--game "/caminho/para/Call of the Wild The Angler"`.
4. Abra o jogo pela Steam normalmente, **sem opções de inicialização**.
5. Em *Opções → Áudio e Idioma*, deixe o idioma do texto em **English**. Com o mod, ele
   aparece como **"Português (BR)"**.

### Desinstalar

```bash
python3 tools/angler_l10n.py uninstall
```

Isso restaura o `game0.tab` e o tamanho original do `game0.arc` byte a byte. Também dá
para usar "Verificar integridade dos arquivos" na Steam.

### Outros comandos

```bash
python3 tools/angler_l10n.py status     # progresso da tradução
python3 tools/angler_l10n.py build      # só gera o arquivo traduzido em build/
python3 tools/angler_l10n.py --version
```

## Perguntas frequentes

**Isso é oficial?** Não. É um projeto de fã, sem ligação com a Expansive Worlds nem com
a Avalanche Studios Group.

**Pode dar ban / afeta o online?** O mod só altera textos exibidos na sua máquina. Não
mexe em jogabilidade, saves ou comunicação com o servidor. Mesmo assim, use por sua conta
e risco.

**Por que não usa a pasta `dropzone`?** Porque ela não funciona na versão vendida do
jogo (detalhes técnicos abaixo).

**Achei um erro de tradução.** Abra uma [issue](../../issues) ou mande um pull request
editando os arquivos em `translations/pt-BR/`.

## Sobre a tradução

A tradução foi gerada com auxílio de IA (Claude), seguindo um
[glossário de pesca](translations/GLOSSARIO.md) para manter os termos consistentes
(vara, molinete, carretilha, fisgada, isca artificial, nomes de peixes…). Uma validação
automática garante que nenhum marcador do jogo (`{a:...}`, `{s:...}`, `<p>`, `<font>`)
foi quebrado. Como **não houve revisão humana completa**, correções da comunidade são
muito bem-vindas.

Os arquivos `translations/pt-BR/*.json` são simples: `{ "chave": "tradução" }`. Depois de
editar, rode `install` de novo.

## Como funciona (técnico)

- O jogo usa o **motor Apex** (Avalanche). Os dados ficam em
  `archives_win64/initial/gameN.tab/.arc` (TAB v3, blocos zlib), e os textos em
  `text/master_eng.stringlookup` (formato **ADF v4**, tipo `StringLookup`: cerca de
  10,5 mil pares chave→texto e 3.800 falas). As chaves usam o hash Jenkins lookup3.
- **A pasta `dropzone` não funciona** na versão de varejo: a função que a monta foi
  compilada vazia, e `--vfs-fs` lê arquivos soltos, mas os `.arc` continuam com
  prioridade.
- Por isso o mod é aplicado **de forma reversível** no próprio arquivo. O texto traduzido
  é anexado ao fim do `game0.arc` (os dados originais não são tocados) e só a entrada
  correspondente no `game0.tab` é reapontada. O `install` guarda `game0.tab.ptbr-orig` e
  `game0.tab.ptbr-size`, usados pelo `uninstall`.
- **O layout do bloco de texto importa:** reordenar as strings faz o jogo travar ou
  mostrar textos vazios. O `build` reescreve as strings **na ordem original**, trocando
  só o conteúdo. Sem traduções, o resultado é idêntico ao original byte a byte.
- **Nenhum arquivo do jogo é distribuído aqui.** O instalador lê o texto original da sua
  própria instalação e aplica as traduções localmente.

Ferramentas: `tools/apex.py` (leitor TAB/ARC), `tools/adf.py` (parser ADF/StringLookup),
`tools/angler_l10n.py` (instalador) e `tools/re/` (utilitários de engenharia reversa
usados na investigação).

---

## English

**Unofficial Brazilian Portuguese (pt-BR) fan translation for _Call of the Wild: The Angler_.**

- **Version 1.0.0**, tested on Steam build **16541670** (AppVersion 2886386), Linux + Proton.
  Windows and Steam Deck should work but haven't been tested yet.
- Translates menus, options, tutorials, dialogue subtitles, codex, journal, missions,
  challenges, shop, gear and fish names (~98.7% of the game's text). AI-assisted
  translation with a fishing glossary; community corrections are welcome.
- **Install:** close the game, then run `python3 tools/angler_l10n.py install` (Windows:
  `py tools\angler_l10n.py install`). Keep the in-game text language set to *English*; it
  will show up as "Português (BR)".
- **Uninstall:** `python3 tools/angler_l10n.py uninstall`, or use *Verify integrity of game
  files* in Steam. After a game update, run `install` again.
- **How it works:** the retail build ignores the `dropzone` override folder, so the
  installer appends the translated `text/master_eng.stringlookup` (ADF v4) to the end of
  `game0.arc` and repoints its entry in `game0.tab`, keeping a backup for uninstall. No
  game files are redistributed.

## Aviso legal / Disclaimer

Projeto de fã, não oficial e sem fins lucrativos. *Call of the Wild: The Angler* e as
marcas relacionadas pertencem à Expansive Worlds / Avalanche Studios Group. Este
repositório não contém arquivos do jogo. O código está sob a licença [MIT](LICENSE).
Unofficial, non-commercial fan project; not affiliated with or endorsed by Expansive
Worlds or Avalanche Studios Group.

**Palavras-chave:** The Angler tradução, Call of the Wild The Angler PT-BR, The Angler
português, tradução The Angler Steam, mod de tradução, legendas em português, jogo de
pesca em português, Brazilian Portuguese translation, pt-BR mod, Apex engine.
