from pathlib import Path
import random
from sric.workspace import Workspace
from authtwin.core import AuthTwinEngine


def test_malformed_json_fuzz_smoke(tmp_path: Path) -> None:
    ws = Workspace.create(tmp_path, "w")
    engine = AuthTwinEngine(ws.root)
    rng = random.Random(1337)
    for i in range(40):
        raw = bytes(rng.randrange(0, 256) for _ in range(rng.randrange(1, 80)))
        path = tmp_path / f"fuzz-{i}.json"
        path.write_bytes(raw)
        try:
            engine.import_json(path)
        except (UnicodeDecodeError, ValueError, TypeError, KeyError):
            pass
