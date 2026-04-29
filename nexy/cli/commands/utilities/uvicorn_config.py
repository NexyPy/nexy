import logging
import os
import traceback
from typing import cast

C = {
    "reset": "\033[0m",
    "dim": "\033[2m",
    "blue": "\033[34m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
}

IGNORED_MESSAGES = [
    "Started server process",
    "Waiting for application startup",
    "Application startup complete",
    "Uvicorn running on",
    "Finished server process",
    "Stopping reloader process",
    "Will watch for changes"
]

# Dictionnaire étendu pour éviter les KeyError (Ajout de 422 et 307)
status_emojis = {
    200: "✓", 
    201: "⊕", 
    304: "⊛", 
    307: "➜",
    400: "△", 
    404: "○", 
    422: "🞫",
    500: "‼", 
}

class NexyFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return not any(ignored in msg for ignored in IGNORED_MESSAGES)

class NexyAccessFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if not record.args or len(record.args) < 5:
            return f"  {C['blue']}ŋ{C['reset']} {C['dim']}[Info]{C['reset']} {record.getMessage()}"

        args = record.args
        if isinstance(args, tuple):
            arg0, arg1, arg2, arg_last = args[0], args[1], args[2], args[-1]
        elif isinstance(args, dict):
            arg0 = args.get("a", "")
            arg1 = args.get("b", "")
            arg2 = args.get("c", "")
            arg_last = args.get("d", 0)
        else:
            return f"  {C['blue']}ŋ{C['reset']} {record.getMessage()}"

        addr = str(arg0)
        host = addr.split(":")[0] if ":" in addr else addr
        port = addr.split(":")[-1] if ":" in addr else "3000"

        method = str(arg1)
        path = str(arg2)
        status_code = int(cast(int, arg_last))

        color = C["green"]
        if 300 <= status_code < 400:
            color = C["cyan"]
        elif 400 <= status_code < 500:
            color = C["yellow"]
        elif status_code >= 500:
            color = C["red"]

        is_socket = "ws" in path or "socket" in path or status_code == 101
        label = f"{C['magenta']}ws{C['reset']} »" if is_socket else f"{color}{method}{C['reset']} »"

        emoji = status_emojis.get(status_code, "⚠️")
        

        return f"{label} {C['dim']}{host}{C['reset']}:{C['blue']}{port}{C['reset']}{color}{path}{C['reset']} , {color}{status_code}{C['reset']} © {emoji}"

class NexyDefaultFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        # Filtrer les messages système inutiles
        if any(ignored in msg for ignored in IGNORED_MESSAGES):
            return ""

        level = record.levelname.capitalize()
        
        # On extrait le nom du fichier et la ligne
        # record.pathname est le chemin complet, on ne garde que le nom du fichier
        file_name = os.path.basename(record.pathname)
        line_no = record.lineno
        
        # Choix de la couleur : rouge pour les erreurs, gris pour le reste
        color = C["red"] if record.levelno >= 40 else C["dim"]
        
        # Construction du préfixe : ŋ [Info] [app.py:12]
        prefix = f"{color}{level}{C['reset']} »"
        
        result = f"{prefix}"
        if record.exc_info:
            # Seulement le dernier frame (fichier avec l'erreur)
            tb_frames = traceback.extract_tb(record.exc_info[2])
            if tb_frames:
                frame = tb_frames[-1]
                file_name = os.path.basename(frame.filename)
                line_no = frame.lineno or 0
                line_text = frame.line.rstrip("\n") if frame.line else ""
                
                # Construire l'affichage façon traceback Python, mais coloré en rouge
                if frame.line:
                    # Indentation originale
                    original_line = line_text
                    indent = len(original_line) - len(original_line.lstrip())
                    code_part = original_line[indent:]
                    
                    caret_indent = " " * (indent + 4)  # 4 espaces pour aligner sous le code
                    caret = "~" * max(1, len(code_part)) + "^~"
                    result += (
                        f"  File \"{frame.filename}\", line {line_no}, in {frame.name or '<module>'}"
                        f"\n    {color}{original_line}{C['reset']}"
                        f"\n{caret_indent}{color}{caret}{C['reset']}"
                    )
                else:
                    result += f"File \"{frame.filename}\", line {line_no}, in {frame.name or '<module>'}"
        return result



NEXY_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "nexy_filter": {"()": NexyFilter}
    },
    "formatters": {
        "access": {"()": NexyAccessFormatter},
        "default": {"()": NexyDefaultFormatter},
    },
    "handlers": {
        "access": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "filters": ["nexy_filter"],
        },
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["nexy_filter"],
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}