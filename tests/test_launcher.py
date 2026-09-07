import importlib.util
from pathlib import Path


def load_tests(loader, tests, pattern):
    root = Path(__file__).resolve().parents[1] / "skills/corpo-launcher/scripts/tests"
    for path in sorted(root.glob("test_*.py")):
        spec = importlib.util.spec_from_file_location("launcher_" + path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        tests.addTests(loader.loadTestsFromModule(module))
    return tests
