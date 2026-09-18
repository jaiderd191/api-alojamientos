import pytest

from app import create_app


@pytest.fixture
def app():
    aplicacion = create_app()
    aplicacion.config.update(TESTING=True)
    return aplicacion


@pytest.fixture
def client(app):
    return app.test_client()