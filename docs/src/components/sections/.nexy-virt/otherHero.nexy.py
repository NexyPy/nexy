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

                                              
                                                     
title : prop[str] = None
description : prop[str] = None
bc = BreadcrumbI18n()