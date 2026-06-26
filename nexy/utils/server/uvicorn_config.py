import linecache
import logging
import os
import traceback
from typing import cast

# ANSI colors for terminal
COLORS = {
    "reset": "\033[0m",
    "dim": "\033[2m",
    "blue": "\033[34m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
}

# Uvicorn system messages to hide for a cleaner console
IGNORED_MESSAGES = [
    "Started server process",
    "Waiting for application startup",
    "Application startup complete",
    "Uvicorn running on",
    "Finished server process",
    "Stopping reloader process",
    "Will watch for changes",
    "Shutting down",
    "connection closed",
    "connection open",
    "Waiting for application shutdown",
    "Application shutdown complete",
    "/_nexy/hmr",
]

# Signs associated with main HTTP status codes (no emojis)
status_indicators = {
    200: "✓",
    201: "+",
    304: "*",
    307: ">",
    400: "!",
    404: "o",
    422: "x",
    500: "!!",
}


class NexyFilter(logging.Filter):
    """Cleaning filter to block redundant initialization logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return not any(ignored in msg for ignored in IGNORED_MESSAGES)


class NexyAccessFormatter(logging.Formatter):
    """Ultra-readable formatter for HTTP requests and WebSocket connections."""

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        if not record.args or len(record.args) < 5:
            return (
                f"  {COLORS['blue']}ŋ{COLORS['reset']} {COLORS['dim']}[Info]{COLORS['reset']} {msg}"
            )

        args = record.args
        if isinstance(args, tuple):
            arg0, arg1, arg2, arg_last = args[0], args[1], args[2], args[-1]
        elif isinstance(args, dict):
            arg0 = args.get("a", "")
            arg1 = args.get("b", "")
            arg2 = args.get("c", "")
            arg_last = args.get("d", 0)
        else:
            return f"  {COLORS['blue']}ŋ{COLORS['reset']} {msg}"

        addr = str(arg0) if arg0 else "unknown"
        host = addr.split(":")[0] if ":" in addr else addr
        port = addr.split(":")[-1] if ":" in addr else "3000"

        method = str(arg1)
        path = str(arg2)

        try:
            status_code = int(cast(int, arg_last))
        except (ValueError, TypeError):
            status_code = 200

        color = COLORS["green"]
        if 300 <= status_code < 400:
            color = COLORS["cyan"]
        elif 400 <= status_code < 500:
            color = COLORS["yellow"]
        elif status_code >= 500:
            color = COLORS["red"]

        is_socket = "ws" in path or "socket" in path or status_code == 101
        label = (
            f"{COLORS['magenta']}ws{COLORS['reset']} »"
            if is_socket
            else f"{color}{method}{COLORS['reset']} »"
        )

        indicator = status_indicators.get(status_code, "!")

        return f"{label} {COLORS['dim']}{host}{COLORS['reset']}:{COLORS['blue']}{port}{COLORS['reset']} {color}{path}{COLORS['reset']} , {color}{status_code}{COLORS['reset']} © {indicator}"


class NexyDefaultFormatter(logging.Formatter):
    """Universal formatter handling errors based on function, class, or module level."""

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        level = record.levelname.capitalize()

        color = COLORS["red"] if record.levelno >= 40 else COLORS["dim"]
        prefix = f"{color}{level}{COLORS['reset']} »"
        result = f"{prefix} {msg}"

        if record.exc_info:
            tb_frames = traceback.extract_tb(record.exc_info[2])
            if tb_frames:
                frame = tb_frames[-1]

                try:
                    file_name = os.path.relpath(frame.filename, start=os.getcwd())
                except Exception:
                    file_name = os.path.basename(frame.filename)

                line_no = frame.lineno or 0
                scope_name = frame.name or "<module>"

                result += f'\n  File "{file_name}", line {line_no}, in {scope_name}\n'

                # --- CONTEXTUAL BLOCK DETECTION ---
                start_line = line_no
                block_indent = None
                is_global_scope = scope_name == "<module>"

                if not is_global_scope:
                    # Walk up to find function or class start
                    while start_line > 1:
                        prev_line = linecache.getline(frame.filename, start_line).rstrip("\n")
                        stripped = prev_line.lstrip()
                        if stripped.startswith(("def ", "class ")):
                            block_indent = len(prev_line) - len(stripped)
                            break
                        start_line -= 1

                # Module-level scope or no structure found
                if block_indent is None:
                    start_line = max(1, line_no - 4)
                    end_line = line_no + 4
                else:
                    # Walk down to find function or class end based on indentation
                    end_line = line_no
                    while True:
                        next_line = linecache.getline(frame.filename, end_line + 1)
                        if not next_line:
                            break

                        next_stripped = next_line.rstrip("\n")
                        if next_stripped.strip():  # Skip empty lines for indentation calculation
                            current_indent = len(next_stripped) - len(next_stripped.lstrip())
                            # Block ends when indentation drops to function/class level
                            if current_indent <= block_indent and end_line >= line_no:
                                break
                        end_line += 1

                # Safety limit: cap large blocks to avoid excessive output
                if (end_line - start_line) > 16:
                    start_line = max(1, line_no - 4)
                    end_line = line_no + 4

                # --- CODE SNIPPET RENDERING ---
                for current_line in range(start_line, end_line + 1):
                    raw_line = linecache.getline(frame.filename, current_line)
                    if not raw_line:
                        continue

                    clean_line = raw_line.rstrip("\n")

                    if current_line == line_no:
                        indent = len(clean_line) - len(clean_line.lstrip())
                        code_part = clean_line[indent:]
                        caret_indent = " " * (indent + 6)
                        caret = "~" * max(1, len(code_part)) + "^~"

                        result += f"    {COLORS['red']}➔{COLORS['reset']}  {COLORS['red']}{clean_line}{COLORS['reset']}\n"
                        result += f"{caret_indent}{COLORS['red']}{caret}{COLORS['reset']}\n"
                    else:
                        result += f"       {COLORS['dim']}{clean_line}{COLORS['reset']}\n"

        return result.rstrip("\n")


# Config ready for uvicorn.run()
NEXY_LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"nexy_filter": {"()": NexyFilter}},
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
