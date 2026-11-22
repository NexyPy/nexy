# Como depuro o código do servidor no Nexy?

Depure o código do servidor de `nx dev` com `breakpoint()` no terminal, ou com VS Code e `debugpy`: o servidor de desenvolvimento executa seu Python em seu próprio processo, então um depurador anexado a ele para em suas páginas, manipuladores de API e ações.

## Como `nx dev` executa seu código

`nx dev` inicia o uvicorn em seu próprio processo, sem um trabalhador separado. Quando um arquivo Python ou uma página `.nexy` muda, ele esquece os módulos do seu projeto e os importa novamente no mesmo processo. Um depurador anexado a `nx dev` portanto permanece anexado durante uma recarga, e um ponto de interrupção definido em um arquivo mantém seu lugar no novo código.

Um arquivo `.nexy` é compilado em um módulo Python em `__nexy__/`, no mesmo caminho, que é o que executa:

<!-- router:fbr,custom -->
| Você escreve | Nexy corre |
|---|---|
| `src/routes/about.nexy` | `__nexy__/src/routes/about.py`, função `About()` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/routes/api/users.py` | o arquivo em si |
<!-- /router -->

<!-- router:modular -->
| Você escreve | Nexy corre |
|---|---|
| `src/apps/users/user_view.nexy` | `__nexy__/src/apps/users/user_view.py` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/apps/users/user_controller.py` | o arquivo em si |
<!-- /router -->

O frontmatter de um arquivo `.nexy` (o Python entre as duas linhas `---`) torna-se o corpo de uma função desse módulo. `__nexy__/` é escrito novamente em cada alteração: nunca edite.

## Pare no terminal com `breakpoint()`

Coloque `breakpoint()` onde você deseja parar, em um arquivo `.py` ou no frontmatter de um arquivo `.nexy`:

<!-- router:fbr,custom -->
```nexy filename="src/rotas/about.nexy"
---
from nexy import useSearchParams

page = useSearchParams().get("page", "1")
breakpoint()
---
<p>Page {{ page }}</p>
```

Abra a página. A requisição aguarda e o terminal de `nx dev` mostra pdb, no módulo compilado:

```text
> /path/to/app/__nexy__/src/routes/about.py(21)About()
-> breakpoint()
(Pdb)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users")
class UserController:
    async def get(self):
        page = "1"
        breakpoint()
        return {"page": page}
```

Abra `/users`. A solicitação espera e o terminal de `nx dev` mostra pdb nessa linha. No frontmatter de uma view, pdb mostra o módulo compilado em `__nexy__/src/apps/`.
<!-- /router -->

Digite `p page` para imprimir um valor, `n` para a próxima linha, `c` para deixar a solicitação continuar. Remova a linha quando terminar: a próxima solicitação para ali novamente.

## Depurar com código VS

Instale `debugpy` no ambiente do projeto:

```bash
uv add --dev debugpy
```

Em seguida, adicione uma configuração de inicialização. `nexy.modules.cli` é o módulo por trás do comando `nx`, então funciona da mesma forma no Linux, macOS e Windows:

```json filename=".vscode/launch.json"
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "nx dev",
      "type": "debugpy",
      "request": "launch",
      "module": "nexy.modules.cli",
      "args": ["dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

Pressione F5. Defina pontos de interrupção em seus arquivos `.py` e no módulo compilado em `__nexy__/` para um arquivo `.nexy`: O VS Code não pode parar em um arquivo `.nexy`, porque não é Python até que seja compilado. Os números de linha do módulo compilado seguem o frontmatter, portanto, um ponto de interrupção pode se mover após a edição da página; `breakpoint()` no frontmatter não.

## Anexar de outro terminal

Para iniciar você mesmo o servidor de desenvolvimento e anexar um depurador posteriormente:

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m nexy.modules.cli dev
```

`--wait-for-client` mantém o início até que um depurador seja anexado; deixe de fora para começar de uma vez. No VS Code, anexe com uma configuração de `"request": "attach"` e `"connect": { "host": "127.0.0.1", "port": 5678 }`.

debugpy pode avisar que "módulos congelados estão sendo usados". Inicie Python com `-Xfrozen_modules=off` (`python -Xfrozen_modules=off -m debugpy ...`) se um ponto de interrupção na biblioteca padrão for perdido; pontos de interrupção em seu próprio código não são afetados.

## Próximas etapas

- [Solução de problemas](troubleshooting.md): os primeiros problemas que as pessoas enfrentam
- [Teste](testing.md): reproduza o bug em um teste depois de encontrá-lo
- [Arquivos .nexy](../views/nexy/README.md): frontmatter, props e modelos
