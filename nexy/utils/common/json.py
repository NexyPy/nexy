def to_json_literal(value: object) -> str:
    """Serialize *value* as a JSON literal (Python bools/None mapped to JS)."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(to_json_literal(item) for item in value) + "]"
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'
