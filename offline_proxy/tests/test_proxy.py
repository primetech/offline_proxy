from aioresponses import aioresponses
from offline_proxy.cache import ProxyCache
from offline_proxy.server import app
import aiohttp
import pytest
import tempfile
import shutil


TEST_BACKEND = 'http://test.com'


@pytest.fixture()
async def app_server(loop, aiohttp_server, tmpdir_factory):
    cache_dir = tmpdir_factory.mktemp('cache')
    proxy_app = await app(backend=TEST_BACKEND, location=cache_dir)
    server = await aiohttp_server(proxy_app)
    server.url = f'http://localhost:{server.port}'
    server.cache_dir = cache_dir
    yield server
    shutil.rmtree(cache_dir)


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

            assert 404 == response.status


    async def test_requests_are_getting_cached(self, app_server):

        with aioresponses(passthrough=[app_server.url]) as mock:
            mock.get(TEST_BACKEND + '/site', status='200', body='OK')

            response, body = await client(app_server.url + '/site')

            cache = ProxyCache(app_server.cache_dir)
            assert 2 == len(cache.cache)
            assert body == cache.get_cached_content_by_url(TEST_BACKEND + '/site')


    async def test_request_returns_cached_content_on_server_error(self, app_server):

        with aioresponses(passthrough=[app_server.url]) as mock:
            mock.get(TEST_BACKEND + '/site', status='200', body='Cached')
            response, body = await client(app_server.url + '/site')

        with aioresponses(passthrough=[app_server.url]) as mock:
            mock.get(TEST_BACKEND + '/site', status='500')
            response, body = await client(app_server.url + '/site')

            assert b'Cached' == body

    async def test_request_returns_not_found_if_not_in_cache(self, app_server):

        with aioresponses(passthrough=[app_server.url]) as mock:
            mock.get(TEST_BACKEND + '/site', status='200', body='Cached')
            response, body = await client(app_server.url + '/site')


        with aioresponses(passthrough=[app_server.url]) as mock:
            mock.get(TEST_BACKEND + '/anothersite', status='500')
            response, body = await client(app_server.url + '/anothersite')

            assert 404 == response.status
