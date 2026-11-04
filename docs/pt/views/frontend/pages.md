# Páginas frontais

Uma **Página** é a unidade básica de um aplicativo Nexy. É um recurso endereçável por URL definido por um arquivo em `src/routes/`. 

Independentemente da estrutura do cliente usada, cada página segue o mesmo ciclo de vida universal e restrições arquitetônicas.

## O ciclo de vida da página

Quando um usuário navega para uma página, Nexy executa as seguintes etapas:

1.  **Route Matching**: O roteador identifica o arquivo correspondente à URL.
2.  **Busca de dados**: O servidor executa a lógica da página (frontmatter Python ou carregador de estrutura) para buscar os dados necessários.
3.  **Composição**: A página é agrupada em seu `layout.nexy` mais próximo (ou layout de estrutura).
4.  **Renderização**: O resultado é renderizado em HTML (via Jinja2, Markdown ou framework SSR).
5.  **Hidratação**: Se a página usar uma estrutura cliente, o navegador anexa a lógica interativa ao HTML estático.

## Roteamento e URLs

O roteamento é estritamente baseado em arquivo. A URL é determinada pelo caminho do arquivo em `src/routes/`, menos a extensão.

### Segmentos Dinâmicos
Para criar uma rota que varia de acordo com o parâmetro (por exemplo, um perfil de usuário), use colchetes:
- `src/routes/user/[id].tsx` → `/user/123`

O valor do segmento (`123`) está disponível para a página através do gancho `useParams()` de `@nexy/client`.

### Grupos de rotas
As pastas entre parênteses são ignoradas pelo roteador, mas permitem agrupar arquivos para fins organizacionais ou layouts compartilhados:
- `src/routes/(auth)/login.tsx` → `/login`

## Metadados da página
Cada página pode definir metadados (título, descrição, tags OpenGraph) que Nexy injeta no shell do documento. Nos arquivos `.nexy`, isso é feito no frontmatter; em arquivos de estrutura, ele é fornecido por meio de uma exportação `metadata`.

## Implementação da Estrutura
Os conceitos acima são universais. Para ver como implementar uma página em seu framework específico, consulte o guia **Diferenças**:

- [Reagir diferenças](../react/differences.md)
- [Diferenças de Vue](../vue/differences.md)
- [Diferenças esbeltas](../svelte/differences.md)
- [Diferenças sólidas](../solid/differences.md)
- [Pré-agir diferenças](../preact/differences.md)