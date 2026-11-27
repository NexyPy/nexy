# Como faço para publicar um módulo no registro Nexy?

Execute `nx publish` de um diretório de módulo com um válido `nx.toml`, um token de registro e cada arquivo declarado pelo manifesto; o comando verifica o lançamento, cria um arquivo e carrega uma versão imutável.

## Prepare o manifesto

Um módulo de origem lista cada arquivo enviado. O arquivo contém `nx.toml` e exatamente esses arquivos.

```toml filename="nx.toml"
name = "@acme/auth"
version = "1.2.0"
kind = "source"

[compatibility]
nexy = ">=2.0.0"
python = ">=3.12"

[dependencies]
python = []
node = []

[source]
files = ["src/auth.py", "src/helpers.py"]
```

O campo `name` deve estar em letras minúsculas `@scope/name`. O campo `version` deve conter três números separados por pontos. Os arquivos devem ser caminhos relativos dentro do módulo. Um módulo de pacote declara `source.package` em vez de `source.files`.

## Verifique antes de enviar

Use `--dry-run` para validar o manifesto, arquivar os arquivos declarados e imprimir a soma de verificação sem fazer upload:

```bash
nx publish --dry-run
```

Uma simulação não precisa de um token. Ele imprime uma linha `warning:` para cada importação relativa que aponta para um arquivo que o manifesto não declara. Por exemplo, `from .helpers import token` em `src/auth.py` precisa de `src/helpers.py` em `source.files`, caso contrário, uma instalação teria uma importação quebrada.

## Defina o token

`nx publish` lê `NEXY_REGISTRY_TOKEN`, então `~/.config/nexy/registry-token`. O token é enviado no cabeçalho `Authorization` e nunca impresso.

```bash
export NEXY_REGISTRY_TOKEN="your-token"
nx publish
```

O arquivo token permite que um futuro `nx login` escreva a mesma credencial. Sem nenhuma das fontes, o comando imprime `error: No registry token` e sai com status 1.

## Publicar

```bash
nx publish
```

O comando imprime o nome, a versão e a soma de verificação SHA-256 do lançamento publicado. Um par de nome e versão é imutável: publicá-lo novamente imprime um erro de conflito. Publique uma nova versão.

## Use outro registro

Por padrão, o comando é postado em `https://registry.nexypy.dev`. Use `--registry` para outro registro, por exemplo, um local durante o desenvolvimento:

```bash
nx publish --registry http://localhost:8000
```

Somente URLs https são aceitos, além de http simples em `localhost`, `127.0.0.1` e `::1`. As respostas transitórias `429` e `5xx` são repetidas duas vezes; um manifesto inválido, um token ausente ou um conflito não será tentado novamente.

## Verifique o lançamento

```bash
nx add @acme/auth@1.2.0
```

Consulte [Instalar módulos](install-modules.md) para atualizações, pins e configurações de confiança.
