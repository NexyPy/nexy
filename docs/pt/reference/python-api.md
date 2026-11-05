# Python API

Cada nome que o Nexy exporta para o seu código Python, por módulo. Um teste verifica esta página em relação ao código em ambas as direções: um nome listado aqui deve existir e um nome que o código exporta deve estar listado aqui.

## `nexy`

Componentes para modelos `.nexy` e ganchos de solicitação.

| Nome | O que é |
|---|---|
| `Audio`, `Video` | jogadores nativos `<audio>` e `<video>`, consulte [componentes](../views/nexy/components.md) |
| `Image` | um `<img>` que carrega lentamente por padrão |
| `Link` | um lado do cliente `<a>` com pré-busca opcional |
| `Import` | importar um componente cliente para uma página `.nexy` |
| `Template` | renderização Jinja2 e Markdown modelos |
| `Vite` | a tag do cliente Vite que toda página precisa |
| `Form` | um espaço reservado sem comportamento: use um `<form>` simples com uma [ação](../guides/actions.md) |
| `usePathname` | o caminho da solicitação atual |
| `useSearchParams` | a string de consulta como um ditado |
| `useParams` | os parâmetros do caminho dinâmico como um ditado, como `useParams()` no cliente |
| `useQuery` | o nome original de `useParams`, mantido para páginas existentes (não lê a string de consulta) |
| `useRequest` | a solicitação atual, para o que os outros ganchos não cobrem |
| `useHeaders` | os cabeçalhos da solicitação como um ditado com nomes em minúsculas |
| `useUrl` | o URL completo: `.scheme`, `.hostname`, `.path`, `.query` |
| `useIsActive` | se um link aponta para a página atual ou para um de seus pais, para uma barra de navegação |
| `useRouter` | `path`, `base_url` e `url_for` da solicitação atual |
| `useSession` | o ditado da sessão, vazio quando as sessões estão desativadas |
| `useCookies` | os cookies de solicitação como um ditado |
| `useToc` | o índice da página atual, como HTML |
| `useViews` | renderiza um arquivo de visualização como `about.tsx` a partir de um manipulador |
| `setMetadata`, `useMetadata` | nomeie o título e as tags de cabeçalho de uma página e escreva-os no layout |
| `redirect`, `permanentRedirect` | envie o visitante para outro lugar (307, 308) e interrompa a solicitação |
| `notFound`, `forbidden`, `unauthorized` | responda 404, 403 ou 401 de qualquer lugar |

Os ganchos funcionam apenas dentro de uma solicitação: consulte [hooks](../routing/fbr/navigation/hooks.md).

## `nexy.http`

O vocabulário HTTP de um manipulador. Importe daqui em vez de FastAPI, para que seus manipuladores dependam do contrato da Nexy.

| Nome | O que é |
|---|---|
| `Request`, `Response` | a solicitação recebida e uma resposta de saída |
| `HTTPException` | pare o manipulador com um status e um `detail` |
| `status` | códigos de status nomeados, como `status.HTTP_404_NOT_FOUND` |
| `Depends` | execute uma função primeiro e passe seu resultado em |
| `Header`, `Cookie`, `Query`, `Path`, `Body` | de onde vem um parâmetro |
| `Form`, `File`, `UploadFile` | campos de formulário e uploads (precisa de `python-multipart`) |
| `BackgroundTasks` | trabalho executado após o envio da resposta |
| `JSONResponse`, `HTMLResponse`, `PlainTextResponse` | respostas com um tipo de conteúdo fixo |
| `RedirectResponse` | um redirecionamento HTTP |
| `redirect`, `permanentRedirect` | levanta um redirecionamento (307, 308) de uma página, um manipulador, um controlador ou um guarda |
| `notFound`, `forbidden`, `unauthorized` | levante um 404, 403 ou 401 dos mesmos lugares |
| `FileResponse`, `StreamingResponse` | responda com um arquivo ou stream |

## `nexy.decorators`

| Nome | O que é |
|---|---|
| `Action` | transformar uma função em um endpoint `POST`, consulte [actions](../guides/actions.md) |
| `revalidate` | informa ao navegador quais páginas uma ação tornou obsoleta |
| `Module`, `Controller` | declara um módulo e um controlador no [roteador modular](../routing/modular/README.md) |
| `Injectable`, `Container`, `Scope` | [injeção de dependência](../routing/modular/dependency-injection.md) e seus tempos de vida |
| `UseGuard`, `Middleware` | proteja ou envolva um manipulador, consulte [guards](../routing/modular/guards-and-metadata.md) |
| `UseRoute`, `useRoute`, `RouteMeta` | nomeie uma rota e descreva-a para OpenAPI |
| `UseResponse`, `ResponseMeta` | descrevem a resposta de uma rota |
| `HTTP_METHODS` | os métodos HTTP que um arquivo manipulador pode definir |
| `ACTIONS_STORE` | o registro de ações, para ferramentais e testes |

## `nexy.testing`

| Nome | O que é |
|---|---|
| `render` | o HTML de um componente `.nexy` para determinados adereços, sem um servidor, consulte [testing](../guides/testing.md) |

## Onde será o próximo

- [Config](config.md): os campos `use*` por trás desses nomes
- [Exceções e erros](exceptions.md): o que cada falha responde
- [Índice de documentação](../README.md): a página do que você está construindo
