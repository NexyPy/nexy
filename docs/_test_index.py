import sys
sys.path.insert(0, '.')
from _convert_mdx import parse_mdx, chunk_body, convert_mdx
from pathlib import Path

path = Path('src/routes/docs/index.mdx').resolve()
frontmatter, body, module_path = parse_mdx(path)
print(f'Module path: {module_path}')
print(f'Frontmatter: {frontmatter[:120]!r}')

chunks = chunk_body(body)
print(f'Chunks: {len(chunks)}')
for i, c in enumerate(chunks):
    ct = c['type']
    cl = len(c['content'])
    ch = c['content'][:80] if ct == 'text' else c['content'][:60]
    print(f'  [{i}] type={ct} len={cl} head={ch!r}')
