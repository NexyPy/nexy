from pathlib import Path
from typing import Optional
from nexy.core.config import Config
from nexy.core.string import StringTransform

class RouteLayout:
    @staticmethod
    def get_closest_import(source_path: str, is_layout: bool = False) -> Optional[str]:
        """
        Remonte l'arborescence pour trouver le layout.nexy le plus proche.
        Si 'is_layout' est True, commence la recherche au dossier parent pour 
        permettre l'emboîtement (Nested Layouts).
        """
        try:
            path = Path(source_path).resolve()
            root = Path(Config.ROUTER_PATH).resolve()
            
            # Point de départ : 
            # Si c'est déjà un layout, on commence la recherche un niveau au-dessus.
            current = path.parent.parent if is_layout else path.parent
            current = current.resolve()

            # On remonte jusqu'à la racine (ou le parent de la racine pour le global)
            limit_dir = root.parent 

            while str(current).startswith(str(limit_dir)):
                layout_candidate = current / "layout.nexy"
                
                # On vérifie que le fichier existe ET que ce n'est pas le fichier source lui-même
                if layout_candidate.is_file() and layout_candidate != path:
                    try:
                        rel_path = layout_candidate.relative_to(Path.cwd())
                    except ValueError:
                        rel_path = layout_candidate

                    # Formatage du module
                    module_path = rel_path.with_suffix("").as_posix().replace("/", ".")
                    namespace = getattr(Config, "NAMESPACE", "__nexy__.").replace("/", ".")
                    
                    full_module = f"{namespace}{module_path}" if namespace.endswith(".") else f"{namespace}.{module_path}"
                    
                    # Normalisation finale via ton StringTransform
                    return StringTransform.normalize_route_path_for_namespace(full_module)

                if current == limit_dir:
                    break
                    
                current = current.parent

        except Exception:
            return None
            
        return None