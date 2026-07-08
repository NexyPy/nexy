import os
import json
import re

LOCALES = {"ar", "de", "es", "fr", "hi", "ja", "ko", "pt", "ru", "zh"}


def strip_markdown(text: str) -> str:
    text = re.sub(r"#+\s+", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"[*_`]", "", text)
    return text.strip()


def extract_title(content: str) -> str:
    match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def detect_locale(filename: str) -> str:
    base = filename.replace(".mdx", "")
    parts = base.split(".")
    if len(parts) > 1 and parts[-1] in LOCALES:
        return parts[-1]
    return "en"


def generate_search_index():
    docs_path = "src/routes/docs"
    search_index = []

    for root, dirs, files in os.walk(docs_path):
        for file in files:
            if not file.endswith(".mdx"):
                continue

            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            title = extract_title(content)
            if not title:
                continue

            locale = detect_locale(file)
            clean_content = strip_markdown(content)

            rel_path = os.path.relpath(file_path, docs_path)
            parts = rel_path.replace("\\", "/").split("/")

            parts = [p for p in parts if not re.match(r"^\(.+\)$", p)]

            last = parts[-1].replace(".mdx", "")
            if locale != "en":
                last = last.replace(f".{locale}", "")
            parts[-1] = last

            href = f"/{locale}/docs/" + "/".join(parts)

            search_index.append({
                "id": len(search_index),
                "title": title,
                "content": clean_content[:300],
                "href": href,
                "lang": locale,
            })

    output_path = "public/search_index.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(search_index, f, indent=2, ensure_ascii=False)

    print(f"Search index generated with {len(search_index)} documents.")


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), "..", "docs"))
    generate_search_index()
