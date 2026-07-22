from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast


class JsonStore:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()
        if not (self.workspace / "workspace.json").is_file():
            raise FileNotFoundError("workspace.json not found; run authtwin init NAME first")
        self.path = self.workspace / "authtwin.json"
        if not self.path.exists():
            self.save(self.empty())

    @staticmethod
    def empty() -> dict[str, Any]:
        return {
            "schema_version": "0.1",
            "actors": [],
            "resources": [],
            "observations": [],
            "invariants": [],
            "findings": [],
            "session_events": [],
            "counterfactual_plans": [],
            "audit": [],
        }

    def load(self) -> dict[str, Any]:
        data = cast(dict[str, Any], json.loads(self.path.read_text(encoding="utf-8")))
        defaults = self.empty()
        for key, value in defaults.items():
            data.setdefault(key, value)
        return data

    def save(self, data: dict[str, Any]) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        tmp.replace(self.path)
