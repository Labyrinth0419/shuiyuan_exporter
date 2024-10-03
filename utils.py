import time
from dataclasses import dataclass
from typing import Dict, List

import requests

cookie_default_path = "./cookies.txt"
def read_cookie(path:str = cookie_default_path):
    with open(path,"r") as f:
        return f.read()
def set_cookie(data:str, path:str = cookie_default_path):
    with open(path,"w",encoding='utf-8') as f:
        f.write(data)


@dataclass
class ReqParam:
    url: str
    headers: Dict
    retries: int = 5
    delay: int = 2


def retry(retries:int, delay:int):
    def decorator(func):
        def wrapper(*arg, **kwargs):
            for i in range(retries):
                try:
                    response = func(*arg, **kwargs)
                    return response
                except Exception as e:
                    nonlocal delay
                    print(f'Exception: {e}, Retry: {i}')
                    if i < retries - 1:
                        time.sleep(delay)
                        delay *= 2
                    else:
                        raise e
        return wrapper
    return decorator

# 目前的版本是在header里面放原始cookie
def make_request(param: ReqParam, once=True):


    def req_once():
        response = requests.get(param.url, headers=param.headers)
        return response

    @retry(retries=param.retries, delay=param.delay)
    def req_multi():
        return req_once()

    if once:
        return req_once()
    return req_multi()