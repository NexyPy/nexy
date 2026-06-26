from nexy.compiler.parser import Parser


def test_fenced_code_block_wrapped_with_raw_in_mdx():
    parser = Parser()
    source = """\
---
---
```html
{{ var }}
```
"""
    result = parser.process(source, current_file="page.mdx")
    assert "{% raw %}" in result.template
    assert "{% endraw %}" in result.template
    assert "```html" in result.template
    assert "{{ var }}" in result.template


def test_fenced_code_block_not_wrapped_in_nexy():
    parser = Parser()
    source = """\
---
---
```html
{{ var }}
```
"""
    result = parser.process(source, current_file="page.nexy")
    assert "{% raw %}" not in result.template
    assert "{% endraw %}" not in result.template


def test_fenced_code_block_survives_endraw_inside():
    parser = Parser()
    source = """\
---
---
```html
{% raw %}
<script>
const data = {{ json_data }};
</script>
{% endraw %}
```
"""
    result = parser.process(source, current_file="page.mdx")
    assert "{{ '{%' }} endraw {{ '%}' }}" in result.template
    assert result.template.count("{% raw %}") == 3
    assert result.template.count("{% endraw %}") == 2
    assert result.template.count("{{ '{%' }}") == 1
    assert result.template.count("{{ '%}' }}") == 1


def test_inline_backtick_escapes_jinja_in_mdx():
    parser = Parser()
    source = """\
---
---
Use `{{ title }}` to render.
"""
    result = parser.process(source, current_file="page.mdx")
    assert "{{ '{{' }}" in result.template
    assert "{{ '}}' }}" in result.template


def test_inline_backtick_not_escaped_in_nexy():
    parser = Parser()
    source = """\
---
---
Use `{{ title }}` to render.
"""
    result = parser.process(source, current_file="page.nexy")
    assert "{{ '{{' }}" not in result.template
    assert "{{ '}}' }}" not in result.template


def test_inline_backtick_without_jinja_unchanged():
    parser = Parser()
    source = """\
---
---
Use `npm run dev` in the terminal.
"""
    result = parser.process(source, current_file="page.mdx")
    assert "npm run dev" in result.template
    assert "{% raw %}" not in result.template
    assert "{{ '{{' }}" not in result.template


def test_mixed_fenced_and_inline_in_mdx():
    parser = Parser()
    source = """\
---
---
Here is `{{ dynamic }}` inline.

```python
print("{{ hello }}")
```
"""
    result = parser.process(source, current_file="page.mdx")
    assert "{% raw %}" in result.template
    assert "{{ '{{' }}" in result.template


def test_multiple_fenced_code_blocks():
    parser = Parser()
    source = """\
---
---
First:

```js
const x = {{ a }};
```

Second:

```js
const y = {{ b }};
```
"""
    result = parser.process(source, current_file="page.mdx")
    assert result.template.count("{% raw %}") == 2
    assert result.template.count("{% endraw %}") == 2


def test_endraw_with_whitespace_control():
    parser = Parser()
    source = """\
---
---
```html
{%- endraw -%}
```
"""
    result = parser.process(source, current_file="page.mdx")
    assert "{{ '{%' }}- endraw -{{ '%}' }}" in result.template
    assert "{% raw %}" in result.template
    assert "{% endraw %}" in result.template


def test_tilde_fenced_code_block():
    parser = Parser()
    source = """\
---
---
~~~html
{{ var }}
~~~
"""
    result = parser.process(source, current_file="page.mdx")
    assert "{% raw %}" in result.template
    assert "~~~html" in result.template
