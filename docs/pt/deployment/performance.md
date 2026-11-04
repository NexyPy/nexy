# Desempenho

O que `nx start` faz por padrão, o que ligar e o que foi medido.

## Padrões

| Preocupação | Padrão | Alterar |
|---|---|---|
| Processa | um trabalhador Uvicorn por CPU no Linux e macOS, um no Windows | `nx start` executa o aplicativo através do Uvicorn |
| Compactação | desativada | `useGZip = {"minimum_size": 1000}` em [Config](../reference/config.md), ou compactação no proxy reverso |
| Arquivos estáticos | servidos com `ETag` e `Last-Modified`, não `Cache-Control` | definir cache de longa duração no proxy reverso ou CDN para pacotes com hash |
| páginas HTML | renderizadas por solicitação, sem cache | [ISR](../rendering/isr.md) com `revalidate = N` |
| Documentos da API | em | `useDocs = False` em produção |
| Nó em tempo de execução | nenhum | `nx build` pré-renderiza componentes do cliente |

## Medido

Uma execução local, um trabalhador Uvicorn, Windows, Python 3.13, conexões keep-alive de uma carga Python
gerador na mesma máquina. Trate os números como uma base para comparar as mudanças, não como uma
comparação com outras estruturas.

| Rota | Simultaneidade | Solicitações por segundo | p50 | p99 |
|---|---|---|---|---|
| Rota JSON FastAPI simples | 16 | ~ 4.500 | 3,4 ms | 5,1 ms |
| Rota Nexy JSON (`src/routes/api/ping.py`) | 16 | ~2.900 | 5,2 ms | 9,8 ms |
| Página Nexy SSR (16 KB, 16 componentes) | 1 | ~500 | 1,9 ms | 3,0 ms |
| Página Nexy SSR (16 KB, 16 componentes) | 64 | ~670 | 94 ms | 126 ms |

Lendo a tabela:

- As próprias camadas do Nexy (contexto de caminho, middleware) custam cerca de um terço do rendimento de uma camada simples
  Rota FastAPI.
- Uma página renderizada pelo servidor custa cerca de 2 ms de CPU, distribuídos por aproximadamente 16 renderizações de modelo (uma por
  componente). Páginas com menos componentes são proporcionalmente mais baratas.
- A produtividade é escalonada com os trabalhadores. No Linux, `nx start` já inicia um por CPU.

## Conselhos práticos

1. Coloque Nginx, Caddy ou a vantagem da sua plataforma na frente: TLS, HTTP/2, Brotli e cache de longa duração para
   `/__nexy__/client/` ativos são seus pontos fortes. Consulte [Implantar](README.md).
2. Use [ISR](../rendering/isr.md) para páginas que mudam menos de uma vez por minuto.
3. Hidrate-se preguiçosamente com [ilhas](../rendering/islands.md) para que o primeiro carregamento envie menos JavaScript.
4. Mantenha o número de `.nexy` componentes por página razoável: cada um é um modelo separado
   renderizar.
5. Meça suas próprias rotas. Um gerador de carga local que mantém as conexões ativas é suficiente para comparar
   duas versões de uma página.

## Próximas etapas

- [Implantar](README.md)
- [Renderização](../rendering/README.md)
- [Configuração](../reference/config.md)