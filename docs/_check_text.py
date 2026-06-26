from pathlib import Path
import re
for name in ['build_and_deploy', 'create_a_projet', 'index']:
    p = Path(f'src/locales/routes/docs/{name}.py')
    if p.exists():
        c = p.read_text()
        m = re.search(r'body_1 = """(.+?)"""', c, re.DOTALL)
        if m:
            print(f'{name}: {m.group(1)[:150]}')
        print()
