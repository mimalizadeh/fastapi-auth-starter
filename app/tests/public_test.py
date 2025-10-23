import json

from app.tests.conftest import logger


def test_00_hello_world(client):
    """Simple request check endpoint : /"""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.text)
    logger.info(data)
    assert 'Hello World' in data['message']
