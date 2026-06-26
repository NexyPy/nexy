import os, re

pages = ['build_and_deploy', 'create_a_projet', 'index', 'projet_structure', 'router-choice']
langs = ['', 'ar', 'de', 'es', 'fr', 'hi', 'ja', 'ko', 'pt', 'ru', 'zh']

def check_file(path):
    content = open(path, encoding='utf-8').read().replace('\r\n', '\n')
    lines = content.split('\n')
    issues = []
    for i in range(len(lines) - 1):
        cur = lines[i].strip()
        nxt = lines[i+1].strip()
        # Ensure blank line after headings
        if re.match(r'^#{1,3}\s', cur) and nxt and not nxt.startswith('#'):
            if not lines[i+1] == '':
                issues.append((i, 'heading', cur[:40]))
        # Ensure blank line after blockquotes  
        if cur.startswith('>') and nxt and not nxt.startswith('>'):
            if not lines[i+1] == '':
                issues.append((i, 'blockquote', cur[:40]))
        # Ensure blank line after paragraphs (non-empty, non-heading, non-code, non-quote, non-list, non-separator)
        if (cur and not cur.startswith(('#', '```', '>', '-', '*', '|', '1.', '2.', '3.', '---')) 
            and not re.match(r'^\d+\.', cur)):
            if nxt and not nxt.startswith(('#', '```', '>', '-', '*', '---')) and not re.match(r'^\d+\.', nxt):
                if not lines[i+1] == '':
                    issues.append((i, 'paragraph', cur[:50]))
        # Ensure blank line after closing code fence
        if cur == '```' and nxt:
            if not lines[i+1] == '':
                issues.append((i, 'code block', '```'))
    return issues

total_issues = 0
for p in pages:
    for l in langs:
        suffix = f'.{l}' if l else ''
        path = f'src/routes/docs/({p})/{p}{suffix}.mdx'
        if not os.path.exists(path):
            continue
        issues = check_file(path)
        if issues:
            for line_num, etype, preview in issues:
                total_issues += 1
                if total_issues <= 30:
                    print(f'{p}{suffix}.mdx line {line_num}: {etype} | {preview}')

print(f'\nTotal issues found: {total_issues}')
