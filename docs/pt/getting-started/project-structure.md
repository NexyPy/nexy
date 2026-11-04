# Estrutura do projeto

Cada arquivo em um projeto Nexy possui um trabalho. Esta página diz qual.

## Nível superior

```text
my-app/
├─ src/
│  ├─ routes/            file-based routes (FBR)
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ apps/              modular router, decorators (optional, next to routes/)
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Para escolher uma pasta, pergunte qual é o arquivo:

- **Algo que o navegador pode abrir** - uma rota: `src/routes/`.
- **Uma peça usada por diversas rotas** - um componente ou módulo: `src/components/`, `src/`.
- **Um arquivo servido como está** - `public/`.
- **Um controlador do roteador modular** - `src/apps/`.
- **Gerado** - `__nexy__/`; nunca edite.

> [!AVISO]
> `src/routes/` é escaneado: um ajudante colocado lá se torna uma rota. Coloque um ajudante que não seja uma rota
> fora de `src/routes/`, ou inicie seu nome com `_`.

## `src/routes/`

Cada arquivo se torna uma rota, exceto os nomes reservados abaixo. O caminho do arquivo menos a extensão é
o URL - consulte [roteamento](../routing/README.md).

| Arquivo | Função |
|---|---|
| `layout.nexy` | envolve páginas irmãs e filhas |
| `errors.nexy` | 500 páginas para o diretório |
| `notfound.nexy` | 404 página para o diretório |
| `dependencies.py` | dependências FastAPI compartilhadas para o diretório |
| `__init__.py` | Marcador de pacote Python |
| `loading.nexy` | reservado - excluído das rotas, mas ainda não tem efeito de tempo de execução |

Cada nome de página também existe por estrutura. Com `react()` configurado, `layout.jsx` e `layout.tsx`
são reservados exatamente como `layout.nexy`. As listas são construídas em `nexy/core/config.py`
(`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`).

> [!NOTA]
> `notfound.nexy` e `errors.nexy` só são instalados quando existe uma cópia no
> rotas raiz. Uma cópia em um subdiretório refina a página para esse prefixo.

## `src/apps/`

O diretório `nexy new` usado para o roteador modular: registradores de controladores, módulos e provedores
suas rotas através de decoradores de `nexy.decorators`, então o agregado `APIRouter` é montado
com `useRouter` em `nexyconfig.py`.

Um projeto pode ter ambos os roteadores: `useRouter` monta o roteador modular e `src/routes/` é verificado
sempre que esse diretório existir. Consulte [roteamento modular](../routing/modular/README.md).

## `public/`

Os arquivos aqui são servidos a partir da raiz do site: `/favicon.ico`, `/robots.txt`, imagens, fontes.

## `__nexy__/`

Gerado por `nx build` (e por `nx dev` para as peças necessárias). Ele contém:

- os módulos de rota compilados, como um pacote Python (`__nexy__/src/routes/...`);
- os pontos de entrada do cliente gerados (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` após uma construção do Vite - ativos, manifesto, HTML pré-renderizado;
- `build-cache.json`.

Trate todo o diretório como descartável: exclua-o e reconstrua-o. Editá-lo manualmente perde a alteração
na próxima construção. Adicione-o a `.gitignore`.

## Próximas etapas

- [Routing](../routing/README.md): como um caminho se torna uma URL
- [Config](../reference/config.md): todas as opções do projeto
- [Frontend](../guides/frontend.md): Vite, estilo e construção do cliente