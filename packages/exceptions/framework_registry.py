from typing import Optional
from .frameworks.base import FrameworkConfig
from .frameworks import DEFAULT, AI_GOV, SOC2, CMMC, ISO27001
from .frameworks.aigov import AI_GOV_ALIASES
from .frameworks.iso27001 import ISO27001_ALIASES


_BUILTINS: dict[str, FrameworkConfig] = {
    "default": DEFAULT,
    "aigov": AI_GOV,
    "soc2": SOC2,
    "cmmc": CMMC,
    "iso 27001": ISO27001,
}

_ALIASES: dict[str, str] = {**AI_GOV_ALIASES, **ISO27001_ALIASES}

_custom: dict[str, FrameworkConfig] = {}


def register(name: str, config: FrameworkConfig, overwrite: bool = False):
    if name in _BUILTINS and not overwrite:
        raise ValueError(f"Built-in framework '{name}' already exists. Use overwrite=True to replace.")
    _custom[name] = config


def get(name: str) -> Optional[FrameworkConfig]:
    canonical = _ALIASES.get(name, name.lower())
    cfg = _custom.get(canonical) or _BUILTINS.get(canonical)
    if cfg:
        return cfg
    return _BUILTINS.get("default")


def list_frameworks() -> list[dict]:
    result = []
    for name, cfg in _BUILTINS.items():
        result.append({"name": name, "display_name": cfg.display_name, "states": cfg.states})
    for name, cfg in _custom.items():
        result.append({"name": name, "display_name": cfg.display_name, "states": cfg.states})
    return result
