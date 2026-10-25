class TemplateResolver:
    """Resolves the template folder name based on project configuration."""

    @staticmethod
    def resolve(config: dict[str, object]) -> str:
        """
        Resolves the template directory name.
        Structure: [project_type]-[router]
        Client framework suffix filtering is handled by the renderer.
        """
        router = "fbr" if config.get("FBRouter") else "modular"
        project_type = config.get("project_type", "web")

        return f"{project_type}-{router}"

    @staticmethod
    def config_for(template: str) -> dict[str, object]:
        """The project configuration a template name stands for.

        ``web-fbr`` is a web project with the file-based router and no client framework;
        ``web-fbr-react`` adds React. Used by ``nx new --template``, which asks nothing.
        """
        project_type, router, *rest = template.split("-")
        return {
            "project_type": project_type,
            "FBRouter": router == "fbr",
            "client_framework": rest[0] if rest else "none",
            "useCSR": False,
            "orm": "None",
            "db_url": None,
            "database": "none",
            "style": "tailwind",
        }
