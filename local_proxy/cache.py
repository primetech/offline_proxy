from diskcache import Cache
import hashlib


class ProxyCache:
    cache = None

    def __init__(self, location, size_limit=2 ** 29):
        """
        A location needs to be provided.
        Default size is 500MB
        """

        self.cache = Cache(location, expire=None, size_limit=size_limit)

    @staticmethod
    def get_key(url):
        return hashlib.md5(url.encode()).hexdigest()

    def add_respone_to_cache(self, url, content_type, body):
        """
        Adds a new item to the cache using the url.
        """

        self.cache[self.get_key(url)] = body
        self.cache[self.get_key(url) + '__type'] = content_type

    def get_cached_content_by_url(self, url):
        return self.cache[self.get_key(url)]            

    def get_cached_content_type_by_url(self, url):
        return self.cache[self.get_key(url) + '__type']            

    def __contains__(self, url):
        return self.get_key(url) in self.cache
