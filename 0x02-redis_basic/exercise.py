#!/usr/bin/env python3
""" Using redis in python """
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """ count function calls """
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ inner wrapper function """
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """ Trace and store function history of inputs/outputs for each call """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """ inner tracer wrapper """
        input = str(args)
        self._redis.rpush(method.__qualname__ + ":inputs", input)
        output = str(method(self, *args, **kwargs))
        self._redis.rpush(method.__qualname__ + ":outputs", output)
        return output
    return wrapper


def replay(fn: Callable):
    """ Display the history of calls of a particular function """
    db = redis.Redis()
    fun_name = fn.__qualname__
    call = db.get(fun_name)
    try:
        call = int(call.decode("utf-8"))
    except Exception:
        call = 0
    print("{} was called {} times:".format(fun_name, call))
    inputs = db.lrange("{}:inputs".format(fun_name), 0, -1)
    outputs = db.lrange("{}:outputs".format(fun_name), 0, -1)
    for inp, outp in zip(inputs, outputs):
        try:
            inp = inp.decode("utf-8")
        except Exception:
            inp = ""
        try:
            outp = outp.decode("utf-8")
        except Exception:
            outp = ""
        print("{}(*{}) -> {}".format(fun_name, inp, outp))


class Cache:
    """ Cache Class """
    def __init__(self):
        """ initialize redis cache object """
        self._redis = redis.Redis(host='localhost', port=6379, db=0)
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """ Cache/store data """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[str, bytes, int, float]:
        """ get data from cache """
        v = self._redis.get(key)
        if fn:
            v = fn(v)
        return v

    def get_str(self, key: str) -> str:
            """ get data from cache as string """
            return self.get(key, lambda d: d.decode('utf-8'))

    def get_int(self, key: str) -> int:
            """ get data from cache as integer """
            return self.get(key, int)
