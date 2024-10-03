import time
import requests
import json
import re
import os


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


with open('cookies.txt') as file:
    cookie_string = file.read()


def atch_replace(path, filename, topic):
    print('文件替换中...')
    file = open(path + filename, 'r', encoding='utf-8')
    md_content = file.read()

    sha1_codes_with_exts = re.findall(r'\[.*?\|attachment\]\(upload://([a-zA-Z0-9]+)\.([a-zA-Z0-9]+)\)', md_content)
    sha1_codes_with_exts = [t[0] + '.' + t[1] for t in sha1_codes_with_exts]
    atch_urls = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Cookie': cookie_string
    }
    not_found_cnt = 0
    i = 0
    while True:
        i += 1
        url_json = 'https://shuiyuan.sjtu.edu.cn/posts/by_number/' + topic + '/' + str(i) + '.json'
        responce_json = make_request_with_retries(url_json, headers=headers)
        if responce_json.status_code == 200:
            not_found_cnt = 0
            data = json.loads(responce_json.text)
            cooked_content = data['cooked']
            match = re.search(r'class="attachment" href="([^"]+)"', cooked_content)
            if match:
                atch_hrefs = match.group(1)
                atch_urls.append('https://shuiyuan.sjtu.edu.cn' + atch_hrefs)
        else:
            not_found_cnt += 1
            if not_found_cnt >= 10:
                break
            continue
    for sha1_with_ext, url in zip(sha1_codes_with_exts, atch_urls):
        md_content = md_content.replace('upload://' + sha1_with_ext, url)
    # 将修改后的内容写回文件
    with open(path + filename, 'w', encoding='utf-8') as file:
        file.write(md_content)
