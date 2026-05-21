import markdown
configs = {'pymdownx.highlight': {'pygments_lang_class': True, 'linenums': False}}
html = markdown.markdown(
    '```{.python filename="app.py"}\nprint("hello")\n```',
    extensions=['pymdownx.superfences', 'pymdownx.highlight', 'attr_list'],
    extension_configs=configs
)
print("WITH attr_list:")
print(repr(html))
print("---")
print(html)
print()

# Without attr_list
html2 = markdown.markdown(
    '```{.python filename="app.py"}\nprint("hello")\n```',
    extensions=['pymdownx.superfences', 'pymdownx.highlight'],
    extension_configs=configs
)
print("WITHOUT attr_list:")
print(repr(html2))
print("---")
print(html2)
