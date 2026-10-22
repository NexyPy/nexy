export default function DeepDocs({ path }: { path: string }) {
  return (
    <main>
      <h1 data-testid="docs">Docs</h1>
      <span data-testid="docs-path">{path}</span>
    </main>
  );
}
