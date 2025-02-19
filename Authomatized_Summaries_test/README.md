# RESUMOS AUTOMATIZADOS

Este repositório permite gerar resumos automatizados de notícias.

## Instruções

1. Crie um environment conda com a versão de Python 3.11.5

2. Crie um arquivo `.env` no diretório raiz e insira sua chave da OpenAI com o nome `OPENAI_API_KEY`.

3. Coloque os arquivos de notícias extraídos no formato `.txt` na pasta `input`.

4. Execute o script `summarizer.py` com o comando:
   ```bash
   python summarizer.py
   ```

5. Os resumos das notícias estarão disponíveis na pasta `output` no formato Word.
