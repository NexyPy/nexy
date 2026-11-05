# Interface

Nexy não envia seu próprio sistema de componentes para o cliente. Ele se baseia em Vite: React, Vue, Svelte, Solid e Preact são todos suportados, e as páginas vanilla funcionam sem nenhuma estrutura de cliente.

## Habilitar uma estrutura

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()   # vue(), svelte(), solid(), preact()
```

`useVite` o padrão é `True`; mantenha-o ativado quando uma estrutura for configurada.

## Arquivos de rota

| Extensão | Renderizado |
|---|---|
| `.nexy`, `.md` | por Nexy na hora da solicitação |
| `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte` | pela estrutura do cliente; pré-renderizado para HTML no momento da construção e então assumido pelo pacote do cliente |

Uma rota de framework é uma página normal, não uma ilha somente cliente: o HTML existe antes do pacote ser executado, então a primeira pintura não espera por JavaScript.

Configuração por estrutura: [React](../views/react/differences.md), [Vue](../views/vue/differences.md), [Svelte](../views/svelte/differences.md), [Solid](../views/solid/differences.md), [Preact](../views/preact/differences.md).

## Desenvolvimento

`nx dev` inicia um servidor em uma porta:

1. o aplicativo recompila as rotas que você altera, servidor e cliente;
2. Vite roda em uma porta interna e serve módulos de framework;
3. Nexy proxies Vite endpoints do Nexy através de sua própria origem.

O navegador só conversa com a porta `3000`. Não há um segundo URL para abrir e nenhum CORS para configurar.

## Construir

`nx build` produz:

- HTML pré-renderizado para rotas de estrutura;
- o pacote de clientes, com ativos abaixo de `__nexy__/client/`;
- as rotas compiladas Python.

Vite constrói o pacote do cliente; o HTML do servidor de cada página do componente é escrito em tempo de construção.

> [!NOTE]
> uma rota cuja renderização do servidor falha é relatada como uma rota somente cliente em vez de falhar em toda a construção.

## Estilo

`nexy new` solicita um modo de estilo e o configura para a estrutura do cliente que você escolher: Tailwind, UnoCSS ou CSS simples. Os tokens de design (cores, fontes, tema escuro) são variáveis ​​CSS em `src/globale.css`, o arquivo que o andaime cria.

| Modo | As páginas iniciais são escritas com |
|---|---|
| Tailwind, UnoCSS | classes utilitárias na marcação, com os tokens mapeados para nomes de classes |
| CSS simples | nomes de classes semânticas e CSS em `src/globale.css` |

Siga o modo do seu projeto ao adicionar uma página: classes utilitárias em um projeto utilitário, CSS em um projeto CSS simples. Mantenha o CSS do componente que os utilitários não podem expressar no bloco `<style>` do componente. Em um projeto de servidor (`.nexy` páginas) UnoCSS lê os `.nexy` arquivos para classes; Tailwind os encontra por conta própria.

## Fontes, imagens, scripts

Coloque arquivos estáticos em `public/` - eles são servidos por `/` tanto no desenvolvimento quanto na produção.

## Próximas etapas

- [Visualizações](../views/README.md): escolha um formato de página
- [Configuração](../reference/config.md): `useFF`, `useVite`, aliases
- [Implantação](../deployment/README.md): o que a compilação produz
