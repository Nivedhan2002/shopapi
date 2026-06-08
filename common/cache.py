from hashlib import sha256

from django.core.cache import cache


def build_cache_key(prefix, raw_key):
    digest = sha256(raw_key.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"


def get_or_set_cache(key, producer, timeout):
    cached_data = cache.get(key)
    if cached_data is not None:
        return cached_data
    data = producer()
    cache.set(key, data, timeout=timeout)
    return data
