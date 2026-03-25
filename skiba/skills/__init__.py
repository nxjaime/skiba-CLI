"""Skill loading entrypoint for Skiba."""

from importlib import import_module
import pkgutil
import os


def load_skills() -> dict:
    skills = {}
    package = __name__
    # Discover modules in the package's directory
    package_path = os.path.dirname(__file__)
    for finder, name, ispkg in pkgutil.iter_modules([package_path]):
        if name == "__init__":
            continue
        mod = import_module(f"{package}.{name}")
        if hasattr(mod, "register"):  # each skill can register itself
            reg = mod.register()
            if isinstance(reg, dict):
                skills.update(reg)
    return skills
