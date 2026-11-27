# Como instalo um módulo do registro?

Execute `nx add @scope/name` em um projeto Nexy para baixar uma versão do registro do módulo, verificá-la e aplicar as alterações declaradas. Adicione `@1.2.0` para fixar uma versão exata.

## Instalar um módulo

Da raiz de um projeto Nexy:

```bash
nx add @acme/auth
nx add @acme/auth@1.2.0
```

`nx add` lê os metadados de lançamento e arquiva de `useModuleRegistry`, verifica a soma de verificação SHA-256 e verifica os intervalos de compatibilidade `nexy` e `python` do módulo. Em seguida, ele grava apenas os arquivos declarados pelo manifesto, adiciona os pacotes Python declarados com `uv add`, adiciona pacotes Node com o gerenciador de pacotes do projeto e aplica os ganchos de configuração a `nexyconfig.py` e `package.json`. As configurações e arquivos existentes permanecem como estão: um arquivo declarado que já existe é ignorado com uma linha `warning:`.

Cada instalação bem-sucedida é registrada em `.nexy/modules.json`. Confirme esse arquivo para que um colega de equipe obtenha a mesma versão do módulo.

## Atualizar um módulo

Para atualizar, execute `nx add @acme/auth` novamente depois que o registro tiver uma versão mais recente ou defina um novo PIN como `@acme/auth@1.3.0`. Um nome não fixado seleciona a versão mais recente da resposta `/versions` do registro. Executar a mesma versão novamente imprime `is already installed` e não altera nada.

## Fixar uma versão

Um pin é exato: `nx add @acme/auth@1.2.0` instala `1.2.0` e nenhuma outra versão. Use um pin no CI e em um commit `.nexy/modules.json` para que cada checkout instale o mesmo código. Sem um pin, uma nova versão altera a próxima instalação.

## Execute migrações

As migrações estão desativadas por padrão. Adicione `--migrate` quando quiser que os comandos declarados de uma versão sejam executados depois que seus arquivos e dependências estiverem no lugar:

```bash
nx add @acme/auth@1.2.0 --migrate
```

Cada comando é impresso antes de ser executado. O projeto precisa de sua ferramenta de migração instalada antes que um módulo possa declará-la.

## Defina o registro e suas regras de confiança

Os padrões estão em `nexyconfig.py`:

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useModuleRegistry = "https://registry.nexypy.dev"
    useRequireSignedModules = False
```

`useModuleRegistry` é o URL base que a CLI lê. Somente URLs https são aceitos, exceto http de loopback para um registro local durante o desenvolvimento. `useRequireSignedModules = True` recusa uma liberação não assinada. Uma liberação que contenha uma assinatura também será recusada até que um verificador esteja disponível; uma vez verificado, `nx add` imprime `Verified by` com a identidade do signatário. Mantenha o padrão `False` apenas para registros em que você confia.
