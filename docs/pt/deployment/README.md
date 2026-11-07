# Implantar

Dois comandos: `nx build` produz os artefatos, `nx start` os atende.

**Antes de começar:** um projeto que é construído localmente com `nx build` e - para páginas do cliente - o conjunto de ferramentas frontend que `nx new` instalou.

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

O tempo de execução precisa apenas de Python. Uvicorn serve o aplicativo compilado e os ativos estáticos; nenhum processo Node e nenhum processo Vite estão envolvidos.

## O que a construção produz

`__nexy__/` contém os módulos de rota compilados, o pacote do cliente em `__nexy__/client/` e o HTML pré-renderizado para rotas de estrutura. Copie o projeto - fonte mais `__nexy__/` - ou construa dentro da imagem.

## Docker

O estágio de construção precisa do Node (para Vite) e Python (para o compilador). O estágio de tempo de execução precisa apenas de Python.

```dockerfile filename="Dockerfile"
FROM node:22-bookworm-slim AS build
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen && uv run nx build

FROM python:3.13-slim
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["nx", "start", "--host", "0.0.0.0", "--port", "8000"]
```

`uv` busca um Python gerenciado quando a imagem base não tem nenhum, e é por isso que o estágio de construção pode começar a partir de uma imagem do Node.

## Atrás de um proxy reverso

Execute `nx start` no localhost e deixe Nginx, Caddy ou o proxy da plataforma encerrar o TLS:

```bash
nx start --host 127.0.0.1 --port 8000
```

Certifique-se de que o proxy encaminhe WebSocket atualizações se você usar manipuladores `SOCKET` e que ele encaminhe o host original - FastAPI cria URLs absolutos a partir dele.

## Verificação de saúde

<!-- router:fbr,custom -->
Adicione um arquivo manipulador, `src/routes/api/health.py` e teste `/api/health` - em vez de uma página que pode ser renderizada lentamente:

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```
<!-- /router -->

<!-- router:modular -->
Adicione um controlador e teste `/health/` - em vez de uma visualização que pode renderizar lentamente:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```

Liste-o no `controllers` do módulo raiz.
<!-- /router -->

### Pontos de extremidade integrados

Um balanceador de carga ou Kubernetes faz duas perguntas: o processo está ativo e pode receber tráfego? Set `useHealth` e Nexy respondem a ambos, sem arquivo manipulador e sem controlador:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useHealth = True
```

| Ponto final | Respostas 200 | Respostas 503 |
|---|---|---|
| `GET /health/live` | enquanto o processo responde | nunca |
| `GET /health/ready` | assim que o aplicativo for iniciado | enquanto ele inicia e quando o servidor pede para parar |

Nexy garante que `/health/ready` acompanha a inicialização e desligamento do servidor.

Nexy garante que ambos os endpoints fiquem fora do log de acesso e do esquema OpenAPI.

Nexy garante que ambos os endpoints respondam antes de `useTrustedHost` e `useHTTPSRedirect`, portanto, uma investigação enviada por HTTP para o endereço de um pod não é recusada.

Por convenção, você mantém suas próprias rotas desativadas `/health/live` e `/health/ready` enquanto `useHealth` está ativado: os pontos finais do Nexy respondem primeiro. `useHealth` é `False` por padrão, portanto, um projeto que não o define mantém os dois caminhos.

Sua aplicação é responsável por verificar do que depende: `/health/ready` relata o ciclo de vida do servidor, não o estado de um banco de dados.

Aponte as sondas de um Kubernetes `Deployment` para eles:

```yaml filename="k8s/deployment.yaml"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
        - name: app
          image: registry.example.com/app:1.0
          ports:
            - containerPort: 8000
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8000
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            periodSeconds: 5
```

## Hospedagem estática

Cada página é HTML, mas Nexy assume um servidor para roteamento e manipuladores de API.

> [!NOTE]
> não há modo de construção `--static`. Uma exportação puramente estática deve ser gerada em seu pipeline a partir da saída `nx build`.

## Lista de verificação

- [] `nx build` no CI, nenhum aviso para rotas que você espera renderizar no servidor
- [] `nx start` sai com o código 1 e não inicia nada, quando um arquivo de rota não pode ser carregado
- [] `NEXY_ACTION_SECRET` definido ou `__nexy__/action.key` mantido com a compilação
- [] `useDocs = False` em produção se o esquema da API não for público
- [] `useTrustedHost` e `useHTTPSRedirect` definidos para implantações públicas
- [] `useHealth = True` quando um balanceador de carga ou Kubernetes investiga o aplicativo
- [ ] `__nexy__/` não confirmado

## Próximas etapas

- [Configuração](../reference/config.md): HTTPS, hosts confiáveis, sessões
- [Frontend](../guides/frontend.md): o que Vite constrói
- [Testando](../guides/testing.md): os comandos para rodar no CI
