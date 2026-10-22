export default function Home() {
  return (
    <main>
      <h1 data-testid="home">Home</h1>
      <a data-nexy-link href="/about">
        About
      </a>
      <a data-nexy-link href="/docs/a/b/c">
        Deep docs
      </a>
      <a href="https://example.com">External</a>
    </main>
  );
}
