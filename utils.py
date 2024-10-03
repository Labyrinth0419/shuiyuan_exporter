import concurrent.futures
import re
import time
import json
from dataclasses import dataclass
from functools import cache
from typing import Dict, List, Callable,Any
from constant import *

import requests

cookie_default_path = "./cookies.txt"
@cache
def read_cookie(path:str = cookie_default_path):
    with open(path,"r") as f:
        return f.read()

def set_cookie(data:str, path:str = cookie_default_path):
    read_cookie.cache_clear()
    with open(path,"w",encoding='utf-8') as f:
        f.write(data)

def validate_cookie(cookie_str):
    # 正则表达式用于匹配 Cookie 名称和值
    cookie_pattern = re.compile(r'^(?:\s*\w+\s*=\\s*[^;]*;)+$')
    return cookie_pattern.match(cookie_str) is not None

@dataclass
class ReqParam:
    url: str
    headers: Dict
    retries: int = 3
    delay: int = 1


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


def parallel_topic(topic:str):
    def decorator(func:Callable[[int], Any]):
        def wrapper():
            nonlocal topic
            url_json = Shuiyuan_Topic + topic + '.json'  # 从原始json中得到楼数
            headers = {
                'User-Agent': UserAgentStr,
                'Cookie': read_cookie()
            }
            req_param = ReqParam(url=url_json, headers=headers)
            response_json = make_request(req_param, once=True)

            try:
                data = json.loads(response_json.text)
                posts_count = data['posts_count']
            except Exception as e:
                raise f"获取楼数失败! 原因:{e}"
            print(f"总楼数 {posts_count}: 正在爬取......")
            result_futures = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for i in range(1, posts_count + 1):
                    fu = executor.submit(func, i)
                    result_futures.append(fu)
                print("工作已加载完毕")
            results = []
            for res in concurrent.futures.as_completed(result_futures):
                try:
                    # print(res)
                    results.append(res.result())
                except Exception as e:
                    print(f'Exception: {e}')
            return results
        return wrapper
    return decorator
