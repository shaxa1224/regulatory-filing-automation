from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class PromptStore:
    base_dir: str

    @staticmethod
    def from_default_location() -> "PromptStore":
        here = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.normpath(os.path.join(here, "..", "prompts"))
        return PromptStore(base_dir=base_dir)

    def load(self, name: str) -> str:
        path = os.path.join(self.base_dir, name)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def render(self, name: str, **variables: str) -> str:
        template = self.load(name)
        try:
            return template.format(**variables).strip()
        except KeyError as e:
            missing = str(e).strip("'")
            raise ValueError(f"Prompt variable missing: {missing}") from e

