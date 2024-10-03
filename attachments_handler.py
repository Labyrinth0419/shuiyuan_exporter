import json
import re
from constant import Shuiyuan_PostByNum, Shuiyuan_Base, UserAgentStr
from utils import read_cookie, make_request, ReqParam


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
    match_urls = []
    headers = {
        'User-Agent': UserAgentStr,
        'Cookie': read_cookie()
    }
    not_found_cnt = 0
    i = 0
    while True:
        i += 1
        url_json = Shuiyuan_PostByNum + topic + '/' + str(i) + '.json'
        param: ReqParam = ReqParam(url=url_json, headers=headers)
        response_json = make_request(param, once=False)
        if response_json.status_code == 200:
            not_found_cnt = 0
            data = json.loads(response_json.text)
            cooked_content = data['cooked']
            match = re.search(r'class="attachment" href="([^"]+)"', cooked_content)
            if match:
                match_hrefs = match.group(1)
                match_urls.append(Shuiyuan_Base + match_hrefs)
        else:
            not_found_cnt += 1
            if not_found_cnt >= 10:
                break
            continue
    for sha1_with_ext, url in zip(sha1_codes_with_exts, match_urls):
        md_content = md_content.replace('upload://' + sha1_with_ext, url)
    # 将修改后的内容写回文件
    with open(path + filename, 'w', encoding='utf-8') as file:
        file.write(md_content)
