from aiohttp.client_exceptions import ClientConnectorError
from urllib.parse import urljoin
import aiohttp.web
import argparse
import logging
import socket
import os


routes = aiohttp.web.RouteTableDef()
logger = logging.getLogger("local proxy")


parser = argparse.ArgumentParser(description='Simple local proxy configuration')
parser.add_argument('--backend', required=True)
parser.add_argument('--port', required=True)


class ServerError(Exception):
    pass


class LocalProxy:

    def __init__(self, backend):
        self.backend = backend

    async def endpoint(self, request):
        target = urljoin(self.backend, request.raw_path)
        logger.info(f'Distpach to: {target}')

        try:
            async with aiohttp.request('GET', target) as response:
                body = await response.content.read()

            if str(response.status).startswith('5'):
                raise ServerError()

            return aiohttp.web.Response(
                body=body,
                status=response.status,
                content_type=response.content_type
            )

        except (socket.gaierror, ClientConnectorError, ServerError):
            # return cashed content
            return aiohttp.web.Response(
                body='Fallback',
                status=200,
                content_type='text/html'
            )


async def app(backend=None):

    env_backend = os.environ.get('BACKEND')
    if backend is None and env_backend is None:
        raise Exception('BACKEND env var is required')
    elif backend is None and env_backend:
        backend = env_backend

    proxy = LocalProxy(backend)
    proxy_app = aiohttp.web.Application()
    proxy_app.add_routes(
        [
            aiohttp.web.get('/{tail:.*}', proxy.endpoint)
        ]
    )
    return proxy_app


if __name__ == "__main__":
    args = parser.parse_args()
    aiohttp.web.run_app(app(args.backend), port=args.port)
