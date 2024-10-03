import time
import requests
import json
import re
import os



def download_image(image_url, headers, output_dir, sha1_name):
    response = requests.get(image_url, headers=headers)
    response.raise_for_status()  # 确保请求成功

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, sha1_name)
    with open(output_path, 'wb') as f:
        f.write(response.content)



open('cookies.txt', 'w')
with open('cookies.txt') as file:
    cookie_string = file.read()

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

def img_replace(path, filename, topic):
    print('图片载入中...')
    file = open(path + filename, 'r', encoding='utf-8')
    md_content = file.read()
    sha1_codes = re.findall(r'!\[.*?\]\(upload:\/\/([a-zA-Z0-9]+)\.[a-zA-Z0-9]+\)', md_content)
    sha1_codes_with_exts = re.findall(r'!\[.*?\]\(upload://([a-zA-Z0-9]+)\.([a-zA-Z0-9]+)\)', md_content)
    sha1_codes_with_exts = [t[0] + '.' + t[1] for t in sha1_codes_with_exts]
    img_names = []
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
            html_content = data['cooked']
            img_srcs = re.findall(r'<img src="(.*?)"', html_content)
            img_sha1s = re.findall(r'<img.*?data-base62-sha1="(.*?)"', html_content)
            for sha1_code in sha1_codes:
                for src, sha1 in zip(img_srcs, img_sha1s):
                    if sha1 == sha1_code:
                        match = re.search(r'\.([a-zA-Z0-9]+)$', src)
                        if not match:
                            continue
                        extension = match.group(1)
                        download_image(src, headers, path + 'images', sha1_code + '.' + extension)
                        img_names.append(sha1_code + '.' + extension)
        else:
            not_found_cnt += 1
            if not_found_cnt >= 10:
                break
            continue
    for sha1_with_ext, name in zip(sha1_codes_with_exts, img_names):
        md_content = md_content.replace(sha1_with_ext, name)
    def replace(match):
        old_link = match.group(0)  # 获取整个匹配的字符串
        new_link = old_link.replace('upload://', './images/')  # 替换链接
        return new_link
    md_content = re.sub(r'!\[.*?\]\(upload://([a-zA-Z0-9]+)\.([a-zA-Z0-9]+)\)', replace, md_content)
    # 将修改后的内容写回文件
    with open(path + filename, 'w', encoding='utf-8') as file:
        file.write(md_content)
