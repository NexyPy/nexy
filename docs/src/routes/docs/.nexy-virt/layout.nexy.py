from typing import Any
prop = Any  # Nexy prop type
__all__: list[str] = []

# Nexy runtime stubs — silences Pylance when nexy package is not in path
try:
    from nexy import Template as __Template, Import as __Import
    from nexy.routers.context import current_request, usePathname
    from nexy.core.config import Config
except ImportError:
    __Template: Any = None
    __Import: Any = None
    current_request: Any = None
    usePathname: Any = None
    Config: Any = None

                                                          
from nexy import usePathname
from src.mocks.docs.sidebar import build_sections
from src.locales.routes.docs.sidebar import SidebarI18n
                                                    
                                                                        
                                         
children:prop[str]
dl = DocsLayoutI18n()
s = SidebarI18n()
pathname = usePathname()

# Build ordered flat list of all sidebar pages (respecting router mode)

is_modular = pathname.startswith('/docs/modular')
mode = 'modular' if is_modular else 'fbr'
all_sections = build_sections(s, mode)
flat_items = []
for section in all_sections:
    for item in section['items']:
        if item.get('href') and item['href'] != '#':
            flat_items.append({**item, 'section': section.get('title', '')})

# Find current page index by matching relative path
rel_path = pathname[len('/docs'):] or '/'
current_idx = -1
for i, item in enumerate(flat_items):
    if item['href'] == rel_path:
        current_idx = i
        break

# Get prev/next items
prev_item = flat_items[current_idx - 1] if current_idx > 0 else None
next_item = flat_items[current_idx + 1] if 0 <= current_idx < len(flat_items) - 1 else None
