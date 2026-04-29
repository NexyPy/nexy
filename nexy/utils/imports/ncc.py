class Ncc:
    def __init__(self, framework: str, path: str, mount_id: str, props: dict, caller:callable) -> None:
        self.props:dict = props
        self.children:str = f"{caller()}"

    def _in_prod(self) -> bool:
        from pathlib import Path
        return Path("__nexy__/nexy.prod").is_file()
    
    def _on_dev(self) -> bool:
        return not self._in_prod()
    


    