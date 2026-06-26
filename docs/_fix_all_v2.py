"""Fix: add blank line after paragraph even before code blocks (but not inside code blocks)."""
import os, re

pages = ['build_and_deploy', 'create_a_projet', 'index', 'projet_structure', 'router-choice']
langs = ['', 'ar', 'de', 'es', 'fr', 'hi', 'ja', 'ko', 'pt', 'ru', 'zh']

total = 0
for p in pages:
    for l in langs:
        suffix = f'.{l}' if l else ''
        path = f'src/routes/docs/({p})/{p}{suffix}.mdx'
        if not os.path.exists(path):
            continue
        content = open(path, encoding='utf-8').read().replace('\r\n', '\n')
        lines = content.split('\n')
        new_lines = []
        in_code = False
        added = 0
        for i in range(len(lines)):
            new_lines.append(lines[i])
            cur = lines[i].strip()
            if not in_code and cur.startswith('```'):
                in_code = True
                continue
            if in_code and cur == '```':
                in_code = False
                continue
            if in_code:
                continue
            if i < len(lines) - 1:
                nxt_raw = lines[i + 1]
                nxt = nxt_raw.strip()
                if not cur:
                    continue
                if cur.startswith('#'):
                    if nxt and not nxt.startswith('#'):
                        if nxt_raw != '':
                            new_lines.append('')
                            added += 1
                elif cur == '```':
                    if nxt:
                        if nxt_raw != '':
                            new_lines.append('')
                            added += 1
                elif (not cur.startswith(('- ', '* ', '---', '|', '```', '>'))
                      and not re.match(r'^\d+\.', cur)):
                    if nxt:
                        if nxt_raw != '':
                            new_lines.append('')
                            added += 1
        if added > 0:
            result = '\n'.join(new_lines)
            open(path, 'w', encoding='utf-8').write(result)
            print(f'{p}{suffix}.mdx: fixed {added}')
            total += added

print(f'\nTotal: {total} blank lines added')
