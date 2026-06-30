from pathlib import Path
from typing import Callable, Dict, List

Progress = Callable[[int, str, str | None], None]

class ReconstructionEngine:
    id = "base"
    name = "Base Engine"
    description = "Abstract reconstruction engine."

    def preflight(self) -> dict:
        raise NotImplementedError

    def run(self, root: Path, frame_files: List[Path], update: Progress, preset: dict) -> List[str]:
        raise NotImplementedError
