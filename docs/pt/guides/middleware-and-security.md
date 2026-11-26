# Middleware e segurança

Nexy é executado em FastAPI e Starlette, portanto seu middleware se aplica. Os comuns são uma linha em `nexyconfig.py`.

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

Cada dicionário `use*` é passado como argumentos de palavra-chave para o middleware Starlette correspondente: `CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `SessionMiddleware`.

## Seu próprio middleware

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` faz aulas de middleware ASGI.

## Limitação de taxa

`useRateLimit` responde `429 Too Many Requests` a um endereço de cliente que envia mais de `requests` solicitações em uma janela de `per` segundos.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useRateLimit = {"requests": 60, "per": 60, "paths": ["/api/", "/_nx_"]}
```

Nexy garante que uma solicitação acima do limite receba um `429` com um cabeçalho `Retry-After`, os segundos restantes na janela, e nunca alcance suas rotas, ações ou middleware.

Nexy garante que sem `useRateLimit` nenhum middleware de limite de taxa será adicionado.

Nexy garante que as sondagens `useHealth` nunca são limitadas.

`paths` é opcional: sem ele todo caminho é limitado. As ações do servidor são atendidas em `/_nx_`, portanto esse prefixo limita todas elas.

A janela é fixa e compartilhada por todos os clientes: as contagens recomeçam a cada múltiplo de `per` segundos. Um cliente pode, portanto, enviar até duas vezes `requests` através da borda de uma janela.

As contagens ficam na memória de cada trabalhador. Com `useWorkers` acima de um, um cliente pode enviar `requests` para cada trabalhador, e as contagens recomeçam quando o servidor for reiniciado.

O endereço do cliente é aquele que o uvicorn fornece à solicitação. Atrás de um proxy reverso na mesma máquina, o uvicorn o lê de `X-Forwarded-For`; para um proxy em outra máquina, liste seu endereço na variável de ambiente `FORWARDED_ALLOW_IPS`, ou cada cliente compartilha o endereço do proxy.

Sua aplicação é responsável por um limite compartilhado por vários trabalhadores ou servidores: um proxy reverso ou uma loja como o Redis.

## HTTPS

Sirva HTTPS diretamente com `useSslKeyfile` e `useSslCertfile` ou encerre o TLS em um proxy reverso e defina `useHTTPSRedirect`. No desenvolvimento, o Vite servidor de desenvolvimento permanece em loopback HTTP atrás da origem Nexy, então o TLS nunca o alcança.

## Lista de verificação de produção

- `useDocs = False` se o esquema OpenAPI não for público.
- `useTrustedHost` definido para seus domínios, para bloquear ataques de cabeçalho de host.
- `useCORS` com origens explícitas, nunca `["*"]` junto com credenciais.
- Um verdadeiro `secret_key` para sessões, lido no ambiente.
- Props passados ​​para os componentes do cliente são escapados por HTML pelo Nexy. Não marque a entrada do usuário `| safe` nos modelos.

## Guardas e dependências

A proteção por rota usa FastAPI dependências. Um `dependencies.py` em um diretório de rotas se aplica a tudo abaixo dele: veja [Dependências](../routing/fbr/dependencies/README.md). No roteador modular use [`@UseGuard`](../routing/modular/guards-and-metadata.md).

## Próximas etapas

- [Configuração](../reference/config.md): todos os campos de middleware
- [Implantar](../deployment/README.md)
- [Desempenho](../deployment/performance.md)
