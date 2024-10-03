import concurrent.futures
import json
import re
from typing import List

from constant import Shuiyuan_PostByNum, Shuiyuan_Base, UserAgentStr, Shuiyuan_Topic
from utils import read_cookie, make_request, ReqParam, parallel_topic


def match_replace(path:str, filename:str, topic:str):
    """
    :param path:
    :param filename:
    :param topic:
    :return:
    """
    print('文件替换中...')
    file = open(path + filename, 'r', encoding='utf-8')
    md_content = file.read()

    sha1_codes_with_exts = re.findall(r'\[.*?\|attachment\]\(upload://([a-zA-Z0-9]+)\.([a-zA-Z0-9]+)\)', md_content)
    sha1_codes_with_exts = [t[0] + '.' + t[1] for t in sha1_codes_with_exts]

    @parallel_topic(topic=topic)
    def fetch_layer_attachment(layer_no: int) -> str:
        try:
            url_json = Shuiyuan_PostByNum + topic + '/' + str(layer_no) + '.json'
            headers = {
                'User-Agent': UserAgentStr,
                'Cookie': read_cookie()
            }
            param = ReqParam(url=url_json, headers=headers)
            response_json = make_request(param, once=False)
            if response_json.status_code == 200:
                data = json.loads(response_json.text)
                cooked_content = data['cooked']
                match = re.search(r'class="attachment" href="([^"]+)"', cooked_content)
                if match:
                    match_hrefs = match.group(1)
                    return Shuiyuan_Base + match_hrefs
            return ""
        except Exception as e:
            print(f"Error processing layer {layer_no}: {e}")
            return ""

    match_urls:List[str] = fetch_layer_attachment()
    # for url in match_urls:
    #     print("match_urls: " + url)
    match_urls = [x for x in match_urls if x != ""]

    for sha1_with_ext, url in zip(sha1_codes_with_exts, match_urls):
        md_content = md_content.replace('upload://' + sha1_with_ext, url)
    # 将修改后的内容写回文件
    with open(path + filename, 'w', encoding='utf-8') as file:
        file.write(md_content)
