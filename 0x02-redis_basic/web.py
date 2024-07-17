#!/usr/bin/env python3
"""Implement a simple cache decorator using Redis."""
import requests
import redis
from functools import wraps
from typing import Callable

# Initialize Redis connection
db = redis.Redis(host='localhost', port=6379, db=0)

def cache(method: Callable) -> Callable:
    """A decorator to cache get_page results."""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper function to cache get_page results."""
        # Increment the access count for the URL
        db.incr(f'count:{url}')

        # Check if the content is already cached
        cached_content = db.get(f'content:{url}')
        if cached_content:
            return cached_content.decode('utf-8')

        # Fetch the content and cache it
        content = method(url)
        db.setex(f'content:{url}', 10, content)
        return content
    return wrapper

@cache
def get_page(url: str) -> str:
    """Fetch the content of a page using its URL."""
    response = requests.get(url)
    return response.text
