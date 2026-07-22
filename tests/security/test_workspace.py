from pathlib import Path
from sric.workspace import Workspace


def test_unsafe_workspace_name_rejected(tmp_path: Path) -> None:
    try:
        Workspace.create(tmp_path, "../escape")
        assert False
    except ValueError:
        pass
