# Como faço para implantar um aplicativo Nexy no Vercel?

Execute `nx add vercel`, confirme os arquivos gerados junto com sua saída `nx build` e aponte o tempo de execução do Vercel Python para `src/server.py:app`.

## Adicione os arquivos da plataforma

Da raiz de um projeto Nexy:

```bash
nx add vercel
nx build
```

`nx add vercel` escreve `src/server.py` e `vercel.json`. Ele também anexa regras de ignorar para os arquivos que mudam enquanto o aplicativo é executado: `__nexy__/build-cache.json`, `__nexy__/server.port`, `__nexy__/.temp/` e `__pycache__/`. A execução do comando novamente mantém os arquivos que já existem e não duplica as regras de ignorar.

## Aponte Vercel no aplicativo

Nas configurações do projeto Vercel, selecione o tempo de execução Python e use `src/server.py:app` como ponto de entrada. Vercel descobre o nome `app` naquele módulo; `nx start` não está envolvido.

O `src/server.py` gerado importa o preguiçoso `nexy.app.app` depois de preparar a pasta de trabalho. Você pode usar o mesmo ponto de entrada com `uvicorn src.server:app` localmente.

## Confirme a saída da compilação

Quando o Vercel não possui comando de construção, ele recebe apenas o que o repositório contém. Confirme `__nexy__/` após cada `nx build`, com as rotas compiladas, o pacote do cliente em `__nexy__/client/` e o manifesto em `__nexy__/client/.vite/manifest.json`.

Mantenha `vite.config.ts` na raiz do projeto e faça o commit. Na produção, Nexy lê o manifesto Vite para escrever a folha de estilo e as tags de script, mas emite essas tags somente quando `vite.config.ts` existe. Sem esse arquivo a página ainda responde 200 e chega sem CSS ou cliente JavaScript.

Não confirme `__nexy__/build-cache.json`: contém caminhos absolutos da máquina que executou a compilação. `__nexy__/server.port` pertence a `nx start` e `__nexy__/.temp/` é o espaço de rascunho.

## Aceite um sistema de arquivos somente leitura

Vercel monta o projeto somente leitura enquanto uma aplicação Python é iniciada. Nexy grava arquivos gerados durante a inicialização, então um `from nexy.app import app` simples pode falhar com `OSError: [Errno 30] Read-only file system`.

O ponto de entrada gerado copia seis itens do projeto em uma pasta temporária gravável antes de importar o aplicativo: `src`, `__nexy__`, `public`, `nexyconfig.py`, `pyproject.toml` e `vite.config.ts`. Ele muda o diretório de trabalho e coloca a cópia primeiro em `sys.path`, porque o Nexy resolve as rotas do diretório atual. Adicione qualquer outro arquivo que seu aplicativo leia em tempo de execução a essa lista manualmente.

## Armazenar ativos estáticos em cache

O `vercel.json` gerado contém as duas regras de cache que um site Nexy implantado usa: arquivos em `/assets/` são imutáveis por um ano, e imagens e fontes em `public/` permanecem atualizadas por um dia com uma janela obsoleta de uma semana durante a revalidação. Adicione outras regras no mesmo arquivo se seu projeto precisar delas.

## Verifique a implantação

Antes de enviar, importe o ponto de entrada e peça uma página:

```bash
uv run python -c "from src.server import app; print(type(app).__name__)"
uv run uvicorn src.server:app
```

Em seguida, abra `/`, uma rota gerada e um arquivo em `/assets/`. Compare a resposta com `nx start` localmente: status, tipo de conteúdo e tamanho devem corresponder. Uma página menor que a local exatamente pelas duas tags de cliente significa que `vite.config.ts` estava faltando no projeto copiado.
