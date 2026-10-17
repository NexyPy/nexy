export default function DemoSlug({ slug = 'unknown' }: { slug?: string }) {
    return (
        <div style={{ padding: '2rem', maxWidth: '480px', margin: '0 auto' }}>
            <h1>Dynamic Route</h1>
            <p>
                <code>slug</code> = <strong>{slug}</strong>
            </p>
            <a href="/demo">Back to /demo</a>
        </div>
    );
}
