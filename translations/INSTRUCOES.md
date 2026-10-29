# Instruções para tradutores (EN -> PT-BR)

Você vai traduzir um lote de textos do jogo de pesca "Call of the Wild: The Angler" para português do Brasil.

1. Leia `translations/GLOSSARIO.md` e siga os termos dele.
2. Gere os lotes com o texto original da sua instalação (`translations/chunks/`, não versionado) e leia o lote `translations/chunks/NNN.json` (objeto JSON `{"chave": "texto em inglês"}`).
3. Escreva `translations/pt-BR/cNNN.json` com EXATAMENTE as mesmas chaves e os valores traduzidos.
   - JSON válido, UTF-8, sem comentários. Escape aspas duplas como \" e quebras de linha como \n.
4. Regras de tradução:
   - Português do Brasil natural, tom de jogo. Diálogos: coloquial e fluido (você, a gente), preserve o tom/humor.
   - Preserve EXATAMENTE os marcadores: `{a:...}`, `{s:...}`, `{n:...}`, `{E}`, `{LMB}` e qualquer `{...}`;
     tags HTML como `<p>`, `</p>`, `<li>`, `<font size='20' color='#cccccc'>`, `</font>`; e `\n`.
     Nunca traduza o conteúdo de dentro de `{...}` ou de atributos de tags.
   - Indicações de som/atuação entre `<...>` como `<Heavy Breathing>`, `<Casting Exertion>`, `<pause>`
     ou `<Sophia Taylor reading from handbook>` podem ser traduzidas (ex.: `<Respiração Pesada>`), mantendo os `< >`.
   - Não traduza nomes próprios de pessoas, lugares, reservas, marcas e modelos (veja o glossário).
   - Mantenha a capitalização no estilo do original (títulos de menu com Iniciais Maiúsculas).
   - Se o texto não precisar de tradução (nome próprio, sigla), repita o original.
   - Não pule nenhuma chave.
5. Valide ao final rodando:
   python3 -I tools/check_chunk.py NNN
   Corrija até o script responder OK.
