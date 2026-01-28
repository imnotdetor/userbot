# loader.py
import os
import importlib
import traceback

def load_plugins():
    for file in os.listdir("plugins"):
        if not file.endswith(".py"):
            continue
        if file.startswith("_"):
            continue
        if file == "__init__.py":
            continue

        module = f"plugins.{file[:-3]}"

        try:
            importlib.import_module(module)
            print(f"✔ {file} imported")
        except Exception:
            print(f"❌ Failed to load {file}")
            traceback.print_exc()
