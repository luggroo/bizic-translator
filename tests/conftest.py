from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption("--model-path", default=None, help="Enable actual pretrained-model tests")
    parser.addoption("--data-root", default=None, help="Path to the unchanged public bizic-dictionary checkout")


@pytest.fixture(scope="session")
def repo(request):
    root = Path(__file__).resolve().parents[1]
    explicit = request.config.getoption("--data-root")
    return Path(explicit) if explicit else root if (root/'site').is_dir() else root/'.cache/bizic-data'


@pytest.fixture(scope="session")
def real_encoder(request):
    path = request.config.getoption("--model-path")
    if not path:
        pytest.skip("Pass --model-path for actual pretrained inference")
    from tujia_lex.embedding import BGEEncoder
    return BGEEncoder(path)
