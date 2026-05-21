GETTING_STARTED: list[dict[str, str]] = [
    {"label": "Architecture", "href": "/getting-started", "status": "active"},
]

FBR: list[dict[str, str]] = [
    {"label": "How FBR works", "href": "/FBR/overview", "status": "active"},
]

MODULAR: list[dict[str, str]] = [
    {"label": "How Modular works", "href": "/Modular/overview", "status": "active"},
]

NEXY_FILE: list[dict[str, str]] = [
    {"label": "File Format", "href": "/nexy-file/file-format", "status": "active"},
]

FRONTEND: list[dict[str, str]] = [
    {"label": "Framework Integration", "href": "/frontend/overview", "status": "active"},
]

REFERENCE: list[dict[str, str]] = [
    {"label": "CLI & Config", "href": "/reference/cli", "status": "active"},
    {"label": "Project Structure", "href": "/reference/structure", "status": "active"},
]

SIDE_BAR = [
    {"caption": "START", "title": "Getting Started", "href": "", "items": GETTING_STARTED},
    {"caption": "FBR", "title": "File Based Routing", "href": "", "items": FBR},
    {"caption": "MODULAR", "title": "Modular Router", "href": "", "items": MODULAR},
    {"caption": ".NEXY", "title": "File Format", "href": "", "items": NEXY_FILE},
    {"caption": "FRONTEND", "title": "Frontend", "href": "", "items": FRONTEND},
    {"caption": "REF", "title": "Reference", "href": "", "items": REFERENCE},
]
