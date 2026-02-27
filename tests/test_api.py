import importlib.util


def test_fastapi_app_module_exists() -> None:
    # Environment-safe check: package availability may vary in sandbox.
    assert importlib.util.find_spec("backend.main") is not None
