import pytest

from airg.data import generate_clients


@pytest.fixture(scope="session")
def records():
    return generate_clients(seed=42)
