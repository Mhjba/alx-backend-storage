#!/usr/bin/env python3
""" implement simple cache decorator using redis db """
import requests
import redis
from functools import wraps
from typing import Callable

db = redis.Redis()


def cache(method: Callable) -> Callable:
    """ A decorator to cache get_page results """
    @wraps(method)
    def wrapper(url: str) -> str:
        """ wrapper function to cache get_page results """
        db.incr(f'count:{url}')
        content = db.get(f'content:{url}')
        if content:
            return content.decode('utf-8')
        content = method(url)
        db.setex(f'content:{url}', 10, content)
        return content
    return wrapper


@cache
def get_page(url: str) -> str:
    """ Fetch the content of a page using its URL """
    return requests.get(url).text
