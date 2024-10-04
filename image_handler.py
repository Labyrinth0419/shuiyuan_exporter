import json
import re
import os

from constant import UserAgentStr, Shuiyuan_PostByNum, Shuiyuan_Base, Shuiyuan_Topic
from utils import ReqParam, make_request, read_cookie, parallel_topic_in_layer


def download_image(param: ReqParam, output_dir:str, sha1_name:str):
    """
    从水源上下载图片到本地(以进行markdown格式替换)
    :param param: 请求参数
    :param output_dir: 保存文件夹
    :param sha1_name: 图片的sha1
    :return:
    """
    response = make_request(param, once=False)
    if response is None:
        return
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, sha1_name)
    with open(output_path, 'wb') as f:
        f.write(response.content)



def img_replace(path:str, filename:str, topic:str):
    """
    替换原始拉取的raw图片内容
    :param path:
    :param filename:
    :param topic:
    :return:
    """
    print('图片载入中...')
    file = open(path + filename, 'r', encoding='utf-8')
    md_content = file.read()
    sha1_codes = re.findall(r'!\[.*?\]\(upload:\/\/([a-zA-Z0-9]+)\.[a-zA-Z0-9]+\)', md_content)
    sha1_codes_with_exts = re.findall(r'!\[.*?\]\(upload://([a-zA-Z0-9]+)\.([a-zA-Z0-9]+)\)', md_content)
    sha1_codes_with_exts = [t[0] + '.' + t[1] for t in sha1_codes_with_exts]

    @parallel_topic_in_layer(topic=topic)
    def fetch_layer_image(layer_no: int):
        url_json = Shuiyuan_PostByNum + topic + '/' + str(layer_no) + '.json'  # 从原始json中抓图片src
        headers = {
            'User-Agent': UserAgentStr,
            'Cookie': read_cookie()
        }
        req_param = ReqParam(url=url_json, headers=headers)
        response_json = make_request(req_param, True)
        ret = []
        if response_json.status_code == 200:
            data = json.loads(response_json.text)
            html_content = data['cooked']
            img_srcs = re.findall(r'<img src="(.*?)"', html_content)
            img_sha1s = re.findall(r'<img.*?data-base62-sha1="(.*?)"', html_content)
            for sha1_code in sha1_codes:
                for src, sha1 in zip(img_srcs, img_sha1s):
                    if sha1 == sha1_code:
                        match = re.search(r'\.([a-zA-Z0-9]+)$', src)
                        if not match:
                            continue
                        url = src if Shuiyuan_Base in src else Shuiyuan_Base[:-1] + src
                        extension = match.group(1)
                        param = ReqParam(url=url, headers=headers)
                        download_image(param=param, output_dir=path + 'images', sha1_name=sha1_code + '.' + extension)
                        ret.append(sha1_code + '.' + extension)
        return ret
    img_names = fetch_layer_image()

    img_names_flatten = [item for sublist in img_names for item in sublist]
    for sha1_with_ext, name in zip(sha1_codes_with_exts, img_names_flatten):
        md_content = md_content.replace(sha1_with_ext, name)

    def replace(matchs):
        old_link = matchs.group(0)  # 获取整个匹配的字符串
        new_link = old_link.replace('upload://', './images/')  # 替换链接
        return new_link

    md_content = re.sub(r'!\[.*?\]\(upload://([a-zA-Z0-9]+)\.([a-zA-Z0-9]+)\)', replace, md_content)
    # 将修改后的内容写回文件
    with open(path + filename, 'w', encoding='utf-8') as file:
        file.write(md_content)
