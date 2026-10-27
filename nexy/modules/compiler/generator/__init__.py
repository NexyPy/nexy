import os

from nexy.core.models import ParserModel
from nexy.errors import NexyCompileError
from nexy.helpers.common.console import console
from nexy.helpers.common.log_line import tagged
from nexy.helpers.fs.vfs import VFS
from nexy.helpers.fs.vfs_packages import write_package_inits

from .logic import LogicGenerator
from .template import TemplateGenerator


class Generator:
    def __init__(self) -> None:
        self.output: str = ""
        self.source: ParserModel | None = None
        self.template = TemplateGenerator()
        self.logic = LogicGenerator()
        self.vfs = VFS()

    def generate(self, output: str, source: ParserModel, source_path: str | None = None) -> bool:
        self.source = source
        try:
            directory = os.path.dirname(output)
            self.logic.generate(template_path=output, source=self.source, source_path=source_path)
            self.template.generate(output=output, source=self.source.template)
            write_package_inits(self.vfs, directory)
            return True
        except Exception as e:
            console.print(tagged("nsc", f"Error writing to file '{output}': {e}", "red"))
            raise NexyCompileError(
                source_path=output,
                message=str(e),
                hint="Fix the template or logic syntax; no output file was written.",
            ) from e


__all__ = ["Generator"]
