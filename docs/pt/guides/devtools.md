# Barra de ferramentas de desenvolvimento

`nexy dev` adiciona uma barra de ferramentas a cada página HTML. Ele fica no canto inferior esquerdo e mostra a rota que você
estão ativados e quanto tempo o servidor demorou e abre em um painel. Nunca faz parte de uma produção
resposta.

| Guia | Mostra |
|---|---|
| Página | URL, rota, manipulador, o arquivo de onde vem (com um link que abre em seu editor), status, horário do servidor, primeiro byte, primeira pintura, conteúdo principal, mudança de layout (classificado em verde, âmbar ou vermelho), DOM pronto |
| Rotas | cada rota do aplicativo com seus métodos, um filtro e o atual marcado; cada um está vinculado ao seu arquivo |
| Erros | erros do servidor desde que `nexy dev` foi iniciado e os erros que o navegador gerou |
| Configurações | tema (corresponde à página, escuro ou claro), posição, tamanho, ocultar, redefinir |

## Mova-o

Arraste o botão: ele segue o ponteiro e se encaixa no canto mais próximo quando você o solta. O painel
abre no meio da tela de onde quer que o botão esteja. A posição é mantida nesta
navegador. Você também pode escolher um canto em **Configurações**.

`Shift` + `Alt` + `D` oculta e mostra a barra de ferramentas. `Esc` fecha o painel.

## Erros

Um erro não detectado no navegador abre uma caixa de diálogo na página com a mensagem e a pilha; com
vários erros, analise-os (1 de 3). Um erro do servidor responde com uma página do mesmo tipo: o
erro, onde foi gerado e o código em torno dele.

## Desligue

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useDevTools = False
```

A barra de ferramentas é um bloco de estilo e um script adicionado antes de `</body>`: sem solicitação externa, sem
dependência. JSON, arquivos e todas as respostas que não sejam HTML são deixadas de lado.

## Próximas etapas

- [Config](../reference/config.md): todas as opções
- [Teste](testing.md): teste uma página ou um componente