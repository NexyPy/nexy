# Middleware e segurança

Nexy é executado em FastAPI e Starlette, portanto seu middleware se aplica. Os comuns são uma linha em
`nexyconfig.py`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {
        "allow_origins": ["https://app.example.com"],
        "allow_methods": ["GET", "POST"],
        "allow_credentials": True,
    }
    useGZip = {"minimum_size": 1000}
    useTrustedHost = {"allowed_hosts": ["example.com", "*.example.com"]}
    useHTTPSRedirect = True
    useSession = {"secret_key": "change-me"}
```

Cada dicionário `use*` é passado como argumentos de palavras-chave para o middleware Starlette correspondente:
`CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `SessionMiddleware`.

## Seu próprio middleware

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` faz aulas de middleware ASGI.

## HTTPS

Sirva HTTPS diretamente com `useSslKeyfile` e `useSslCertfile` ou encerre o TLS em um proxy reverso
e defina `useHTTPSRedirect`. No desenvolvimento, o servidor de desenvolvimento Vite permanece em loopback HTTP atrás do
Origem Nexy, então o TLS nunca a alcança.

## Lista de verificação de produção

- `useDocs = False` se o esquema OpenAPI não deve ser público.
- `useTrustedHost` definido para seus domínios, para bloquear ataques de cabeçalho de host.
- `useCORS` com origens explícitas, nunca `["*"]` junto com credenciais.
- Um verdadeiro `secret_key` para sessões, lido no ambiente.
- Props passados ​​para componentes do cliente são escapados por HTML pelo Nexy. Não marque a entrada do usuário `| safe` em
  modelos.

## Guardas e dependências

A proteção por rota usa dependências FastAPI. Um `dependencies.py` em um diretório de rotas se aplica a
tudo abaixo: veja [Dependências](../routing/fbr/dependencies/README.md). No uso do roteador modular
[`@UseGuard`](../routing/modular/guards-and-metadata.md).

## Próximas etapas

- [Config](../reference/config.md): todos os campos de middleware
- [Implantar](../deployment/README.md)
- [Desempenho](../deployment/performance.md)