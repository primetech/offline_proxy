offline_proxy
=============

The purpose of this package is to provide a simple proxy which stores
the response of successful requests locally on the disk.

The main use case is provide a solid web service for TV screens showing
informations from a website. In a environment with a really instable Internet connection, or WIFI connection.
Thus this package keeps everything a simple as possible

Limitations
-----------

- Only GET requests are handled.
- Stores only the url, content_type and body. All other header infos get lost
- No performance improvement at all - in fact it adds a lot of overhead


Development
-----------

Run single worker locally for debugging purposes.

```
python offline_proxy/server.py --backend=https://some.site --port=8080 --storage=/path/to/cache
```


Install and run tests:

```
pip install .[tests]
pytest
```


Deployment
----------

```
pip install offline_proxy
```

See https://docs.aiohttp.org/en/stable/deployment.html for detailed informations

Here is an example using gunicorn, which is shipped with this packages too:

```
gunicorn offline_proxy.server:app --bind localhost:8080 --worker-class aiohttp.GunicornWebWorker --workers 4 --env PROXY_BACKEND="https://some.site" --env PROXY_CACHE_LOCATION=/path/to/cache
```

The service requires to configurations in your environment:

- PROXY_BACKEND
- PROXY_CACHE_LOCATION

They need to be present, otherwise the server doesn't start.

