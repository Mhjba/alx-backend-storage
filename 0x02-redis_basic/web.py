#!/usr/bin/env python3
""" implement simple cache decorator using redis """
import redis
import requests
from functools import wraps
from typing import Callable


redis_cl = redis.Redis()


def data_cacher(method: Callable) -> Callable:
    """ Caches the output """
    @wraps(method)
    def wrapper(url) -> str:
        """ wrapper function """
        redis_cl.incr(f'count:{url}')
        result = redis_cl.get(f'result:{url}')
        if result:
            return result.decode('utf-8')
        result = method(url)
        redis_cl.set(f'count:{url}', 0)
        redis_cl.setex(f'result:{url}', 10, result)
        return result
    return wrapper


@data_cacher
def get_page(url: str) -> str:
    """ Returns the content of a URL """
    return requests.get(url).text
