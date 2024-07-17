#!/usr/bin/env python3
""" Module declares a redis class and methods """
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps

DataTypes = Union[str, bytes, int, float]
ConversionFn = Callable[[bytes], DataTypes]


def count_calls(method: Callable) -> Callable:
    """ count how many times methods of Cache class are called """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ wrap the decorated function and return the wrapper """
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """ store the history of inputs and outputs for a particular function"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ inner tracer wrapper """
        fun_name = method.__qualname__
        self._redis.rpush(f'{fun_name}:inputs', str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(f'{fun_name}:outputs', str(result))
        return result
    return wrapper


def replay(method: Callable) -> None:
    """ Display the history of calls of a particular fun. """
    fun_name = method.__qualname__
    db = redis.Redis()
    times = int(db.get(fun_name))
    inputs = db.lrange(f'{fun_name}:inputs', 0, -1)
    outputs = db.lrange(f'{fun_name}:outputs', 0, -1)

    print(f'{fun_name} was called {times} times:')
    for inp, outp in zip(inputs, outputs):
        inp, outp = inp.decode('utf-8'), outp.decode('utf-8')
        print(f'{fun_name}(*{inp}) -> {outp}')


class Cache:
    """ declares a Cache redis class"""

    def __init__(self):
        """ declares a Cache redis class """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: DataTypes) -> str:
        """ takes a data argument and returns a string """
        ar_key = str(uuid.uuid1())
        self._redis.set(ar_key, data)
        return ar_key

    def get(self, key: str, fn: Optional[Callable] = None) -> DataTypes:
        """ convert the data back to the desired format """
        value = self._redis.get(key)
        if fn:
            return fn(value)
        return value

    def get_str(self, key: str) -> str:
        """ parametrize Cache.get with correct conversion function """
        value = self._redis.get(key)
        return value.decode("utf-8")

    def get_int(self, key: str) -> int:
        """ parametrize Cache.get with correct conversion function """
        return self.get(key, int)
