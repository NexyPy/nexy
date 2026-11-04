# CSR (renderização do lado do cliente)

## Definição

CSR entrega a navegação para o navegador: após o primeiro documento, a movimentação entre as páginas não é mais solicitada
o servidor para HTML. No Nexy é uma decisão de **projeto**, não uma página um - `useCSR = True` vira o
todo o aplicativo é roteado pelo cliente.

## Como funciona

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

O projeto então muda de forma:

| | Modo servidor (`False`) | Modo cliente (`True`) |
|---|---|---|
| Rotas | `.nexy`, `.md`, `.mdx` | `.tsx`, `.jsx`, `.vue`, `.svelte` |
| Documento | `layout.nexy` | a raiz `layout.tsx` / `.vue` / `.svelte` possui `<html>`, `<head>`, `<body>` |
| Componentes do cliente | ilhas dentro de uma página | as próprias páginas |
| `.nexy` sob `src/routes/` | o formato de página | rejeitado antes de `nx dev`, `nx start` e `nx build` |
| Navegação | uma solicitação completa por link | o roteador cliente |

`.md` e `.mdx` permanecem válidos: Nexy os renderiza no servidor dentro do layout do cliente, e o
o roteador do cliente assume a partir daí. `.py` manipuladores ficam próximos às rotas e são atendidos pelo FastAPI.

## Ciclo de vida de renderização

1. A solicitação chega ao roteador baseado em arquivo, que encontra a rota correspondente e seus layouts.
2. O layout raiz renderiza o **documento inteiro** no Node - a primeira resposta já carrega o
   real `<html>`, não uma concha vazia.
3. Nexy injeta os ativos do cliente e uma descrição JSON da página antes de `</body>`.
4. O navegador hidrata esse documento. Os layouts aninhados mantêm seu estado a partir de então.
5. Um link para outra rota é tratado pelo roteador cliente: nenhuma solicitação de documento, a página é
   renderizado no navegador.

No desenvolvimento, o documento é renderizado sob demanda pelo servidor de desenvolvimento Vite. Na produção é
renderizado uma vez na construção: uma rota estática obtém seu documento, uma rota dinâmica obtém um por declarado
parâmetro estático ou shell - os layouts em torno de uma página vazia - quando não declara nenhum.

## Quando usar

- Painéis, editores, qualquer coisa que se comporte como um aplicativo.
- Uma API Python com um aplicativo cliente no topo.
- Uma página onde cada interação é local e uma viagem de ida e volta seria sentida.

## Configuração

| Configuração | Valor |
|---|---|
| `useFF` | obrigatório: `useCSR` sem uma estrutura de cliente é rejeitado |
| `useCSR` | `True` |
| `useRouter` | deve ficar desligado: o roteador modular é rejeitado em modo cliente |

Arquivos e pastas começando com `_` ou `.` são ignorados por essas verificações.

## Exemplo

```tsx filename="src/routes/layout.tsx"
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head><title>My app</title></head>
      <body>{children}</body>
    </html>
  )
}
```

```tsx filename="src/rotas/index.tsx"
export default function Home() {
  return <h1>Home</h1>
}
```

## Limitações

- **O projeto inteiro.** Você não pode misturar uma página CSR em um projeto em modo servidor: escolha o modo para
  o aplicativo e use [islands](islands.md) para as partes interativas de uma página em modo servidor.
- **Não há `.nexy` rotas.** Qualquer coisa que você escreveu em `.nexy` deve se tornar um componente da estrutura.
- **Os dados do servidor passam pelos endpoints.** Uma rota do cliente não pode ler o banco de dados no momento da renderização; isso
  chama um manipulador `.py` ou uma [Action](../guides/actions.md).
- **Uma rota dinâmica precisa de um parâmetro estático declarado ou começa a partir de um shell.** Exportar
  `getStaticParams()` da página - os nomes Next.js `getStaticPaths` e `generateStaticParams`
  também são aceitos - ter um documento por valor. Sem ele, o shell carrega os layouts e
  não a página: a página aparece quando o navegador é executado.
- **CSR não é uma página em branco, nem um SPA.** O primeiro documento é renderizado pelo servidor; isso
  é a navegação que acontece no navegador.

## Próximas etapas

- [Modo servidor e modo cliente](../routing/fbr/modes.md): as verificações e os arquivos rejeitados
- [Layouts](../routing/fbr/layouts/README.md): qual arquivo possui o documento
- [SSR](ssr.md): o padrão, página por página
- [Frontend](../guides/frontend.md): o servidor de desenvolvimento e a compilação do cliente