# Front-end

Nexy não envia seu próprio sistema de componentes para o cliente. Baseia-se em Vite: React, Vue, Svelte,
Solid e Preact são todos suportados, e as páginas vanilla funcionam sem nenhuma estrutura de cliente.

## Ativar uma estrutura

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()   # vue(), svelte(), solid(), preact()
```

`useVite` o padrão é `True`; mantenha-o ativado quando uma estrutura for configurada.

## Arquivos de rota

| Extensão | Renderizada |
|---|---|
| `.nexy`, `.md` | por Nexy no momento da solicitação |
| `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte` | pela estrutura do cliente; pré-renderizado para HTML no momento da construção e então assumido pelo pacote do cliente |

Uma rota de estrutura é uma página normal, não uma ilha somente cliente: o HTML existe antes da execução do pacote,
então a primeira pintura não espera pelo JavaScript.

Configuração por estrutura: [React](../views/react/differences.md), [Vue](../views/vue/differences.md),
[Esbelto](../views/svelte/differences.md), [Sólido](../views/solid/differences.md),
[Pré-agir](../views/preact/differences.md).

## Desenvolvimento

`nx dev` inicia um servidor em uma porta:

1. o aplicativo recompila as rotas que você altera, servidor e cliente;
2. Vite roda em uma porta interna e serve módulos de framework;
3. Nexy faz proxy dos endpoints do Vite através de sua própria origem.

O navegador só conversa com a porta `3000`. Não há um segundo URL para abrir e nenhum CORS para configurar.

## Construir

`nx build` produz:

- HTML pré-renderizado para rotas de framework;
- o pacote de clientes, com ativos sob `__nexy__/client/`;
- as rotas Python compiladas.

Vite cuida do pacote do cliente; SSR HTML é produzido por arquivo por esbuild.

> [!NOTA]
> uma rota cuja renderização do servidor falha é relatada como uma rota somente cliente em vez de
> falha em toda a compilação.

## Estilo

`nexy new` solicita um modo de estilo e o configura para a estrutura do cliente escolhida: Tailwind,
UnoCSS ou CSS simples. Os tokens de design (cores, fontes, tema escuro) são variáveis CSS em
`src/globale.css`, o arquivo que o scaffold cria.

| Modo | As páginas iniciais são escritas com |
|---|---|
| Tailwind, UnoCSS | classes utilitárias na marcação, com os tokens mapeados para nomes de classes |
| CSS simples | nomes de classes semânticas e CSS em `src/globale.css` |

Siga o modo do seu projeto ao adicionar uma página: classes utilitárias em um projeto utilitário, CSS em um
CSS simples um. Mantenha o CSS do componente que os utilitários não podem expressar no bloco `<style>` do componente.
Em um projeto de servidor (`.nexy` páginas) UnoCSS lê os `.nexy` arquivos para classes; Tailwind os encontra
por conta própria.

## Fontes, imagens, scripts

Coloque arquivos estáticos em `public/` - eles são servidos por `/` tanto no desenvolvimento quanto na produção.

## Próximas etapas

- [Visualizações](../views/README.md): escolha um formato de página
- [Config](../reference/config.md): `useFF`, `useVite`, aliases
- [Deploy](../deployment/README.md): o que a compilação produz