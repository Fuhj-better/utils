import pickle
import os
import time
from functools import wraps

def cache(cache_file):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            cache_key = (args, tuple(sorted(kwargs.items())))

            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    try:
                        cache = pickle.load(f)
                    except (EOFError, pickle.UnpicklingError):
                        cache = {}
            else:
                cache = {}

            if cache_key in cache:
                print(f"Load cache：{func.__name__}")
                return cache[cache_key]


            print(f"Sava cache：{func.__name__}")
            result = func(*args, **kwargs)

 
            cache[cache_key] = result
            with open(cache_file, 'wb') as f:
                pickle.dump(cache, f)

            return result
        return wrapper
    return decorator



