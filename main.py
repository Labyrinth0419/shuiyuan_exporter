import os
import time
import requests
import json
import re
from bs4 import BeautifulSoup
from image_dealer import *
from attachments_dealer import *

def make_request_with_retries(url, headers, retries=5, delay=2):
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers)
            return response
        except requests.exceptions.RequestException as e:
            if i < retries - 1:
                time.sleep(delay)
                delay *= 2  # 可以增加延迟来避免频繁请求
            else:
                raise e

def short_post(path, topic, cookie_string):
    url_topic = 'https://shuiyuan.sjtu.edu.cn/t/topic/' + topic
    url_raw = 'https://shuiyuan.sjtu.edu.cn/raw/' + topic
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Cookie': cookie_string
    }
    response_raw = make_request_with_retries(url_raw, headers=headers)
    response_topic = make_request_with_retries(url_topic, headers=headers)
    title = 'Empty'
    if response_topic.status_code == 200:
        content_topic = response_topic.text
        soup = BeautifulSoup(content_topic, 'html.parser')
        title = soup.title.string if soup.title else 'Empty'
    if response_raw.status_code == 200:
        content_raw = response_raw.text
    filename = (title + '.md').replace('/', ' or ')
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    filename = topic[0:] + ' ' + filename
    with open(path + filename, 'w', encoding='utf-8') as file:
        file.write(content_raw)
    return filename


def long_post(path, topic, cookie_string):
    topic = topic[1:]
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Cookie': cookie_string
    }
    url_topic = 'https://shuiyuan.sjtu.edu.cn/t/topic/' + topic
    url_cooked = 'https://shuiyuan.sjtu.edu.cn/posts/by_number/' + topic + '.json'
    response_topic = make_request_with_retries(url_topic, headers=headers)
    title = 'Empty'
    if response_topic.status_code == 200:
        content_topic = response_topic.text
        soup = BeautifulSoup(content_topic, 'html.parser')
        title = soup.title.string if soup.title else 'Empty'
    filename = (str(title) + '.md').replace('/', ' or ')
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    filename = topic + ' ' + filename
    with open(path + filename, 'w', encoding='utf-8') as file:
        file.write("")

    not_found_cnt = 0
    i = 0
    while True:
        i += 1
        url_raw = 'https://shuiyuan.sjtu.edu.cn/raw/' + topic + '/' + str(i)
        response_raw = make_request_with_retries(url_raw, headers=headers)
        if response_raw.status_code == 200:
            not_found_cnt = 0
            content_raw = f'post #{i}\n' + response_raw.text + "\n\n-----------------------------------\n\n"
        else:
            not_found_cnt += 1
            if not_found_cnt >= 10:
                break
            continue
        with open(path + filename, 'a', encoding='utf-8') as file:
            file.write(content_raw)

        if i % 50 == 0:
            print(filename + ": post #" + str(i) + " successfully saved!")
    return filename


def export(cookie_string):
    topic = input('请输入帖子编号:(退出请输入"???", 多于100楼的帖子请输入"L+帖子编号")\n')
    if topic == "???":
        return False
    print('文字备份中...')
    topic = str(topic)
    path = './posts/' + (topic[1:] if topic[0] == 'L' else topic) + '/'
    os.makedirs(path, exist_ok=True)
    if topic[0] == 'L':
        filename = long_post(path=path, topic=topic, cookie_string=cookie_string )
    else:
        filename = short_post(path=path, topic=topic, cookie_string=cookie_string)
    img_replace(path=path, filename=filename, topic=(topic[1:] if topic[0] == "L" else topic))
    atch_replace(path= path, filename=filename, topic=(topic[1:] if topic[0] == "L" else topic))
    print(f'编号为 #{topic[1:] if topic[0] == "L" else topic} 的帖子已备份为本地文件：{filename}\n')
    return True

def cookie_set():
    while True:
        cookies = input('请输入cookie:(如果使用上次结果请输入"!!!",退出输入"???")\n')
        if cookies == "???":
            return None
        if cookies == "!!!":
            if os.path.isfile('./cookies.txt') or os.path.getsize('./cookies.txt') == 0:
                print('您还未设置cookie！')
                continue
            else:
                with open('./cookies.txt', 'r', encoding='utf-8') as f:
                    cookie_string = f.read()
                break
        else:
            with open('./cookies.txt', 'w', encoding='utf-8') as f:
                f.write(cookies)
                cookie_string = cookies
            break
    return cookie_string

def run():
    cookie_string = cookie_set()
    while cookie_string:
        if not export(cookie_string):
            break


run()

