from aiohttp.client_exceptions import ClientConnectorError
from local_proxy.cache import ProxyCache
from urllib.parse import urljoin
import aiohttp.web
import argparse
import logging
import os
import socket


routes = aiohttp.web.RouteTableDef()
logger = logging.getLogger("local proxy")


parser = argparse.ArgumentParser(description='Simple local proxy configuration')
parser.add_argument('--backend', required=True)
parser.add_argument('--location', required=True)
parser.add_argument('--port', required=True)


class ServerError(Exception):
    pass


class LocalProxy:

    backend = None
    cache = None

    def __init__(self, backend, location):
        self.backend = backend
        self.cache = ProxyCache(location)

    async def endpoint(self, request):
        target = urljoin(self.backend, request.raw_path)
        logger.info(f'Distpach to: {target}')


        try:
            async with aiohttp.request('GET', target) as response:
                body = await response.content.read()

            if str(response.status).startswith('5'):
                raise ServerError()

            content_type = response.content_type
            self.cache.add_respone_to_cache(target, content_type, body)
            return aiohttp.web.Response(
                body=body,
                status=response.status,
                content_type=response.content_type
            )

        except (socket.gaierror, ClientConnectorError, ServerError):

            if target in self.cache:
                return aiohttp.web.Response(
                    body=self.cache.get_cached_content_by_url(target),
                    status=200,
                    content_type=self.cache.get_cached_content_type_by_url(target)
                )
            else:
                return aiohttp.web.Response(
                    status=404,
                    content_type='text/plain'
                )



async def app(backend=None, location=None):

    env_backend = os.environ.get('PROXY_BACKEND')
    env_location = os.environ.get('PROXY_CACHE_LOCATION')

    if backend is None and env_backend is None:
        raise Exception('PROXY_BACKEND env var is required')
    elif backend is None and env_backend:
        backend = env_backend

    if location is None and env_location is None:
        raise Exception('PROXY_CACHE_LOCATION env var is required')
    elif location is None and env_location:
        location = env_location


    proxy = LocalProxy(backend, location)
    proxy_app = aiohttp.web.Application()
    proxy_app.add_routes(
        [
            aiohttp.web.get('/{tail:.*}', proxy.endpoint)
        ]
    )
    return proxy_app


if __name__ == "__main__":
    args = parser.parse_args()
    aiohttp.web.run_app(app(args.backend, args.location), port=args.port)
