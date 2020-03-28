from aioresponses import aioresponses
from local_proxy.server import app
import aiohttp
import pytest


TEST_BACKEND = 'http://test.com'


@pytest.fixture
async def app_server(loop, aiohttp_server):
    proxy_app = await app(backend=TEST_BACKEND)
    server = await aiohttp_server(proxy_app)
    server.url = f'http://localhost:{server.port}'
    return server


async def client(endpoint):
    async with aiohttp.request('GET', endpoint) as response:
        body = await response.content.read()
    return response, body


class TestProxy:

    async def test_app_needs_a_backend(self):
        with pytest.raises(Exception):
            await app()

    async def test_wildcard_enpoint(self, app_server):

        with aioresponses(passthrough=[app_server.url]) as mock:
            mock.get(rf'{TEST_BACKEND}.*', status='200', body='OK')

            endpoints = [
                '/test',
                '/test/',
                '/test/long/path',
                '/test?param=something',
                '/something?param=test&param2=test2'
            ]
            for endpoint in endpoints:
                response, body = await client(app_server.url + endpoint)
                assert endpoint == response.url.raw_path_qs

    async def test_return_fallback_response_on_backend_error(self, app_server):

        with aioresponses(passthrough=[app_server.url]) as mock:
            mock.get(TEST_BACKEND + '/error', status='500')

            response, body = await client(app_server.url + '/error')

            assert response.status == 200
            assert body == b'Fallback'


