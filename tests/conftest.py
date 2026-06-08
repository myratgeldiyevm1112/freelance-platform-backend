import pytest
from app.core.limiter import limiter

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    storage = getattr(limiter, "_storage", None)
    if storage and hasattr(storage, "reset"):
        storage.reset()
    yield
