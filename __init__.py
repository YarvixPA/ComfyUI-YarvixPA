import importlib.util
import sys
from pathlib import Path
import traceback

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}


def load_module(module_name: str, file_path: str):
    """Load a Python module from a .py file using importlib."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        raise ImportError(f"Failed to create spec for {module_name} ({file_path})")

    module = importlib.util.module_from_spec(spec)
    # Avoid duplicate imports if the module is reloaded
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _module_name_for(path: Path, base_pkg: str, nodes_path: Path) -> str:
    """Convert a file path to a package-style module name (e.g., nodes.sub.package.module)."""
    relative = path.relative_to(nodes_path)  # e.g. 'sub/package/module.py'
    parts = list(relative.with_suffix('').parts)  # ['sub', 'package', 'module']
    return ".".join([base_pkg, *parts]) if parts else base_pkg


def load_nodes():
    """
    Load all .py modules inside 'nodes' and its subfolders,
    including subpackage __init__.py files (except the root __init__.py).
    Merge NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS if defined.
    """
    base_pkg = "nodes"
    nodes_path = Path(__file__).parent / base_pkg

    if not nodes_path.is_dir():
        print(f"[load_nodes] Directory '{nodes_path}' does not exist.")
        return

    # Collect all .py files recursively, excluding the root __init__.py
    py_files = [
        file for file in nodes_path.rglob("*.py")
        if not (file.name == "__init__.py" and file.parent == nodes_path)
    ]

    # Stable sort for reproducibility (by relative path)
    py_files.sort(key=lambda p: str(p.relative_to(nodes_path)))

    for file in py_files:
        try:
            module_name = _module_name_for(file, base_pkg, nodes_path)
            module = load_module(module_name, str(file))

            # Merge NODE_CLASS_MAPPINGS if present
            mod_class_map = getattr(module, "NODE_CLASS_MAPPINGS", {})
            if isinstance(mod_class_map, dict):
                for key in mod_class_map:
                    if key in NODE_CLASS_MAPPINGS:
                        print(f"[load_nodes] Warning: duplicate key '{key}' in NODE_CLASS_MAPPINGS "
                              f"(module {module_name}). It will be overwritten.")
                NODE_CLASS_MAPPINGS.update(mod_class_map)

            # Merge NODE_DISPLAY_NAME_MAPPINGS if present
            mod_display_map = getattr(module, "NODE_DISPLAY_NAME_MAPPINGS", {})
            if isinstance(mod_display_map, dict):
                for key in mod_display_map:
                    if key in NODE_DISPLAY_NAME_MAPPINGS:
                        print(f"[load_nodes] Warning: duplicate key '{key}' in NODE_DISPLAY_NAME_MAPPINGS "
                              f"(module {module_name}). It will be overwritten.")
                NODE_DISPLAY_NAME_MAPPINGS.update(mod_display_map)

        except Exception as e:
            relative = file.relative_to(nodes_path)
            print(f"[load_nodes] Error loading {relative}: {e}\n{traceback.format_exc()}")


# Execute the loader
load_nodes()

# Web configuration: export directory properly
WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
