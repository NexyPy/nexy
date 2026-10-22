import { useState } from 'react';

export default function Demo() {
    const [count, setCount] = useState(0);
    return (
        <div style={{ padding: '2rem', maxWidth: '480px', margin: '0 auto' }}>
            <h1>Nexy TSX Route</h1>
            <p>This page is a client-navigated <code>.tsx</code> route (React).</p>
            <button
                onClick={() => setCount((c) => c + 1)}
                style={{
                    padding: '0.5rem 1rem',
                    marginRight: '0.5rem',
                    borderRadius: '8px',
                    border: '1px solid #888',
                    background: 'transparent',
                    cursor: 'pointer',
                }}
            >
                count is {count}
            </button>
            <a href="/demo/hello">Go to /demo/hello</a>
        </div>
    );
}
