# Changelog

## [1.0.0] — 2026-10-29

Primeira versão pública.

- Tradução PT-BR de ~9.400 textos (98,7% do texto do jogo): menus, opções, tutoriais,
  legendas de diálogo, códex, diário, missões, desafios, loja, equipamentos e peixes.
- Glossário de termos de pesca e nomes de espécies em português.
- Instalador reversível (`install` / `uninstall`), que aplica o texto traduzido no
  `game0.arc`/`game0.tab` com backup. A pasta `dropzone` não funciona na versão de varejo.
- Reconstrução do `StringLookup` (ADF v4) preservando a ordem original das strings.
  Sem traduções, o resultado é idêntico ao original byte a byte.
- Detecção automática da pasta do jogo nas bibliotecas da Steam (Linux, Steam Deck e
  Windows) e aviso quando o build do jogo é diferente do testado.
- Testado no build Steam 16541670 (AppVersion 2886386), Linux + Proton.
