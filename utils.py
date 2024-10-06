import concurrent.futures
import os.path
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
    """
    阅读path为 './cookies.txt' 的文件并写入。
    如果对应的cookie不存在，则返回空字符串
    """
    if not os.path.exists(path):
        return ""
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

def parallel_topic_in_page(topic:str, limit: int):
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
                pages = data['posts_count'] // limit + (1 if data['posts_count'] % limit != 0 else 0)
            except Exception as e:
                raise Exception(f"获取页数失败! 原因:{e}")
            print(f"总页数 {pages}: 正在爬取......")
            result_futures = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for i in range(1, pages + 1):
                    fu = executor.submit(func, i)
                    result_futures.append(fu)
                print("工作已加载完毕")
            results = []
            for cnt, res in enumerate(concurrent.futures.as_completed(result_futures)):
                try:
                    # print(res)
                    results.append(res.result())
                    if cnt % 10 == 0:
                        print(f"--- 已完成工作: {cnt}/{pages}")
                except Exception as e:
                    print(f'Exception: {e}')
            return results
        return wrapper
    return decorator

def code_block_fix(content:str)->str:
    def find_end_pos(content:str, start:int=None, end:int=None)->int:
        layer_pos = content.find(layer_pagination, start, end)
        details_pos = content.find(details_end_pagination, start, end)
        if layer_pos == -1 and details_pos == -1:
            return -1
        elif layer_pos == -1:
            return details_pos
        elif details_pos == -1:
            return layer_pos
        else:
            return min(layer_pos, details_pos)
    fixed_content = ""
    insert_pos = []
    code_block_start = 0
    while True:
        code_block_start = content.find(code_block_pagination, code_block_start)
        if code_block_start == -1:
            break
        code_block_start += 1
        code_block_end = content.find(code_block_pagination, code_block_start)
        #layer_pos = content.find(layer_pagination, code_block_start)
        end_pos = find_end_pos(content, start=code_block_start)
        if end_pos == -1:
            break
        elif code_block_end == -1:
            insert_pos.append(end_pos)
            break
        elif end_pos < code_block_end:
            insert_pos.append(end_pos)
            code_block_start = code_block_end
        elif end_pos > code_block_end:
            code_block_start = end_pos
    if not insert_pos:
        return content
    for i in range(len(insert_pos)):
        fixed_content += content[:insert_pos[i]] + code_block_pagination + "\n"
    fixed_content += content[insert_pos[-1]:]
    return fixed_content