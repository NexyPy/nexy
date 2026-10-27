// Components of the Solid document scenario; compiled twice (server and client) by solid_document.mjs.
import { createSignal } from "solid-js";

export function RootLayout(props) {
  return (
    <html lang="fr" class="dark">
      <head>
        <title>Layout title</title>
      </head>
      <body class="antialiased">
        <header id="head">Header</header>
        <main>{props.children}</main>
      </body>
    </html>
  );
}
export function Nested(props) {
  return <section class="nested">{props.children}</section>;
}
export function Home() {
  const [count, setCount] = createSignal(0);
  return (
    <div id="home">
      <p>Home</p>
      <button id="counter" onClick={() => setCount(count() + 1)}>
        count {count()}
      </button>
    </div>
  );
}
export function About() {
  return <p id="about">About</p>;
}
