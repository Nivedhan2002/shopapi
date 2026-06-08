from common.cache import build_cache_key, get_or_set_cache

PUBLIC_PRODUCT_LIST_CACHE_TIMEOUT = 60 * 5


def get_cached_public_product_response(request, producer):
    cache_key = build_cache_key("public-products", request.get_full_path())
    return get_or_set_cache(cache_key, producer, PUBLIC_PRODUCT_LIST_CACHE_TIMEOUT)
