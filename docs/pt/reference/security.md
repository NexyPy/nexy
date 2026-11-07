# Segurança

Como o Nexy mantém sua própria superfície de ataque pequena, quais versões ele requer e como verificar um projeto.

## Pisos de versão

Nexy depende de FastAPI, Starlette, Jinja2, Vite e React. Um piso é a versão mais baixa que o Nexy permite; cada um responde a um comunicado publicado.

| Pacote | Piso | Por que |
|---|---|---|
| `starlette` | 1.0.1 | CVE-2026-48710 (BadHost): um cabeçalho `Host` criado altera o caminho Starlette dos relatórios para o middleware, que ignora a autorização escrita em `request.url.path`. Listado como explorado pela CISA. |
| `fastapi` | 0,133,0 | a primeira versão que aceita um Starlette fixo |
| `jinja2` | 3.1.6 | escape da sandbox através do filtro `attr` (CVE-2025-27516) |
| `vite` (projetos de andaimes) | 6.4.3 | `server.fs.deny` bypass em caminhos alternativos do Windows (CVE-2026-53571); o desvio de string de consulta anterior (CVE-2026-39364) afeta apenas Vite 7.1-7.3.1 e 8.0.0-8.0.4 |
| `react`, `react-dom` | 19.2.5 | os avisos de 2026 React dizem respeito aos pacotes `react-server-dom-*`, que Nexy não usa; o chão mantém a linha remendada |

Verifique suas versões resolvidas:

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## Regras que Nexy segue

- **Nunca confie no cabeçalho Host para caminhos.** Nexy lê `scope["path"]`, não `request.url.path`, em seu próprio middleware (middleware de diretório). Faça o mesmo no seu.
- **Escape do que chega ao HTML.** Props passados ​​para componentes do cliente, `Link` atributos, `Image`, `Audio` e `Video` atributos, âncoras de índice e `HTTPException` detalhes são todos escapados de HTML. Um modelo `.nexy` não escapa por si só: escreva `{{ value | e }}` para qualquer valor que venha de um visitante ou do banco de dados, e nunca `| safe` na entrada do usuário.
- **Os endpoints do desenvolvedor são somente loopback e estreitos.** O endpoint de renderização de desenvolvimento (`/__nexy__/render`) aceita apenas arquivos em `src/routes/` com uma extensão `.tsx` ou `.jsx` e é acessível apenas por meio do servidor de desenvolvimento, que recusa cabeçalhos `Host` estrangeiros.
- **Os detalhes do erro não vazam.** Uma página de erro que falha mostra apenas o código de status.
- **As respostas de produção carregam cabeçalhos seguros.** `X-Content-Type-Options: nosniff` e `Referrer-Policy: strict-origin-when-cross-origin`, a menos que seu código defina o seu próprio. O cabeçalho `Server` não é enviado. Adicione `Strict-Transport-Security` e um `Content-Security-Policy` em seu proxy ou middleware: eles dependem do seu domínio.
- **Uma falha mostra uma referência, não o erro.** Consulte [Páginas de erro](../routing/fbr/errors/README.md#unhandled-exceptions).
- **Nenhum `eval` e nenhum `shell=True` no código Python do Nexy.** Programas externos são executados com uma lista de argumentos.

## Executando as auditorias

```bash
python scripts/audit_dependencies.py        # Python dependencies against the lock
npm audit                                    # in a scaffolded project
uv run bandit -r nexy -c .bandit             # static analysis of Nexy itself
```

O próprio repositório do Nexy executa a primeira e a terceira em suas verificações. Um novo aviso em um andar acima é tratado elevando o piso em `pyproject.toml` ou no andaime `package.json`, e então regenerando a fechadura.

## Implantando com segurança

- Defina `useTrustedHost` para seus domínios: ele rejeita cabeçalhos `Host` inesperados antes de qualquer rota.
- Não exponha o servidor de desenvolvimento Vite: `nx dev` o mantém em loopback atrás da origem Nexy.
- Defina `useDocs = False` se o esquema da API não deve ser público.

Consulte [Middleware e segurança](../guides/middleware-and-security.md).

## Fontes

- [CVE-2026-48710 (BadHost) em Starlette](https://www.penligent.ai/hackinglabs/cve-2026-48710/)
- [Vite consultivo GHSA-fx2h-pf6j-xcff](https://github.com/advisories/GHSA-fx2h-pf6j-xcff) e [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [Jinja2 CVE-2025-27516](https://advisories.gitlab.com/pypi/jinja2/CVE-2025-27516/)
- [React pacotes de servidores CVE-2026-44907](https://www.wiz.io/vulnerability-database/cve/cve-2026-44907)

## Próximas etapas

- [Middleware e segurança](../guides/middleware-and-security.md)
- [Implantar](../deployment/README.md)
- [Configuração](config.md)
