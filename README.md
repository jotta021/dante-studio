# Dante Studio — API MVP

Protótipo FastAPI para animar o Dante usando imagem + áudio e o motor [SadTalker](https://github.com/OpenTalker/SadTalker).

**Estado:** código inicial. Ainda não implantado nem testado com os pesos do SadTalker. O GitHub hospeda apenas o código, não processa os vídeos.

## Instalação

1. Prepare Python 3.10, FFmpeg e SadTalker com seus modelos conforme o projeto original.
2. Configure SADTALKER_DIR para a pasta que contém inference.py.
3. Instale dependências: `pip install -r requirements.txt`.
4. Defina uma chave forte em DANTE_API_KEY. Não coloque chaves no GitHub.
5. Execute: `uvicorn app:app --host 127.0.0.1 --port 8000`.

## Uso

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H 'x-api-key: SUA_CHAVE' \
  -F 'image=@dante.png' \
  -F 'audio=@fala.wav'
```

A resposta contém job_id. Para baixar:
```bash
curl -H 'x-api-key: SUA_CHAVE' http://127.0.0.1:8000/videos/JOB_ID -o dante.mp4
```

## Limitações

- Ainda sem painel web, voz automática, legendas ou integração com TikTok.
- O processamento é síncrono; requer servidor ou computador compatível.
- Não exponha diretamente na internet sem HTTPS, fila, limites de uso e controles adicionais.
- Os arquivos gerados ficam armazenados até serem removidos manualmente.
- A qualidade com o rosto robótico do Dante ainda precisa ser validada.
