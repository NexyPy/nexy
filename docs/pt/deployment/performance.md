# Desempenho

O que `nx start` faz por padrão, o que ativar e com que rapidez um projeto inicia e responde.

## Padrões

| Preocupação | Padrão | Mude |
|---|---|---|
| Processos | um Uvicorn trabalhador por CPU no Linux e macOS, um no Windows | `nx start` executa o aplicativo por meio de Uvicorn |
| Compressão | desligado | `useGZip = {"minimum_size": 1000}` em [Configuração](../reference/config.md), ou compactar no proxy reverso |
| Arquivos estáticos | servido com `ETag` e `Last-Modified`, não `Cache-Control` | definir cache de longa duração no proxy reverso ou CDN para pacotes com hash |
| Páginas HTML | renderizado por solicitação, sem cache | [ISR](../rendering/isr.md) com `revalidate = N` |
| Documentos da API | ligado | `useDocs = False` em produção |
| Nó em tempo de execução | nenhum | `nx build` pré-renderiza componentes do cliente |

As duas opções da tabela em `nexyconfig.py` e ISR em uma página:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useGZip = {"minimum_size": 1000}
    useDocs = False
```

<!-- router:fbr,custom -->
```nexy filename="src/rotas/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```
<!-- /router -->

<!-- router:modular -->
ISR é um modo de páginas de arquivo: uma visualização retornada por um controlador é renderizada em cada solicitação.
<!-- /router -->

## Inicialização, primeira página e recompilação

Quanto tempo leva um projeto com uma `.nexy` página, mediana de 5 execuções, cada uma em um novo processo Python:

| Medir | Mediana | O que cobre |
|---|---|---|
| Inicialização | 460ms | de um novo processo para uma aplicação pronta para responder: importações, varredura de rotas, compilação |
| Primeira página | 554ms | o mesmo, mais a primeira solicitação para `/` e seu HTML |
| Recompilar uma página | 1,8ms | compilar a página novamente após uma edição, em um processo que já está em execução |

Medido em um AMD Ryzen 5 4500U, Linux, 6 CPUs, Python 3.13.15. Recompilar é o que `nx dev` faz para o Python lado de uma mudança; uma recarga do navegador também paga pelo gráfico do módulo de Vite e pela renderização do próprio navegador, portanto, não é um tempo de recarga.

Meça sua própria máquina com o script que escreveu a tabela:

```bash
python scripts/measure_speed.py --runs 5
```

O fluxo de trabalho `Speed` executa-o em cada push para `main` e grava a mesma tabela no resumo da execução, em um executor Ubuntu hospedado no GitHub.

## Solicitações por segundo

Uma execução local, um Uvicorn trabalhador, Windows, Python 3.13, conexões keep-alive de um gerador de carga Python na mesma máquina. Trate os números como uma base para comparar as mudanças, e não como uma referência em relação a outras estruturas.

A rota Nexy JSON da tabela é este arquivo:

<!-- router:fbr,custom -->
```python filename="src/routes/api/ping.py"
async def GET():
    return {"ok": True}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/ping_controller.py"
from nexy.decorators import Controller


@Controller("/api/ping")
class PingController:
    async def get(self):
        return {"ok": True}
```

As figuras abaixo foram medidas com a rota do arquivo. Meça um controlador da mesma maneira antes de confiar nele.
<!-- /router -->

| Rota | Simultaneidade | Solicitações por segundo | p50 | p99 |
|---|---|---|---|---|
| Rota JSON simples FastAPI | 16 | ~4.500 | 3,4ms | 5,1ms |
| Rota Nexy JSON (`src/routes/api/ping.py`) | 16 | ~2.900 | 5,2ms | 9,8ms |
| Página Nexy SSR (16 KB, 16 componentes) | 1 | ~500 | 1,9ms | 3,0ms |
| Página Nexy SSR (16 KB, 16 componentes) | 64 | ~670 | 94ms | 126ms |

Lendo a tabela:

- As próprias camadas do Nexy (contexto de caminho, middleware) custam cerca de um terço do rendimento de uma rota FastAPI simples.
- Uma página renderizada pelo servidor custa cerca de 2 ms de CPU, distribuídos por aproximadamente 16 renderizações de modelo (uma por componente). Páginas com menos componentes são proporcionalmente mais baratas.
- O rendimento é escalonado com os trabalhadores. No Linux, `nx start` já inicia um por CPU.

## Conselhos práticos

1. Coloque Nginx, Caddy ou a vantagem da sua plataforma na frente: TLS, HTTP/2, Brotli e cache de longa duração para `/__nexy__/client/` ativos são seus pontos fortes. Consulte [Implantar](README.md).
2. Use [ISR](../rendering/isr.md) para páginas que mudam menos de uma vez por minuto.
3. Hidrate-se preguiçosamente com [ilhas](../rendering/islands.md) para que a primeira carga seja enviada menos JavaScript.
4. Mantenha o número de `.nexy` componentes por página razoável: cada um é uma renderização de modelo separada.
5. Meça suas próprias rotas. Um gerador de carga local que mantém as conexões ativas é suficiente para comparar duas versões de uma página.

Conselho 1 com Nginx: os pacotes de clientes com hash são armazenados em cache por um ano, o restante vai para Nexy.

```nginx filename="/etc/nginx/conf.d/my-app.conf"
server {
    listen 443 ssl http2;
    server_name example.com;

    location /__nexy__/client/ {
        proxy_pass http://127.0.0.1:3000;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Próximas etapas

- [Implantar](README.md)
- [Renderização](../rendering/README.md)
- [Configuração](../reference/config.md)
