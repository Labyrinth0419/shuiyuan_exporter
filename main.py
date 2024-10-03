from bs4 import BeautifulSoup
from image_handler import *
from attachments_handler import *
from constant import *
from utils import *


def short_post(path:str, topic:str, cookie_string:str)->str:
    """
    获取小于100楼的帖子
    :param path: save file path
    :param topic: shuiyuan topic id
    :param cookie_string: raw cookie string, get by read_cookie()
    :return: saved filename
    """
    url_topic = Shuiyuan_Topic + topic
    url_raw = Shuiyuan_Raw + topic
    headers = {
        'User-Agent': UserAgentStr,
        'Cookie': cookie_string
    }
    response_raw = make_request(param=ReqParam(url_raw, headers), once=False)
    response_topic = make_request(param=ReqParam(url_topic, headers), once=False)
    title = 'Empty'
    content_raw = ""
    if response_topic.status_code == 200:
        content_topic = response_topic.text
        soup = BeautifulSoup(content_topic, 'html.parser')
        title = soup.title.string if soup.title else 'Empty'
    if response_raw.status_code == 200:
        content_raw = response_raw.text
    filename = (title + '.md').replace('/', ' or ')
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    filename = topic + '-' + filename
    with open(path + filename, 'w', encoding='utf-8') as f:
        f.write(content_raw)
    return filename


def long_post(path:str, topic:str, cookie_string:str)->str:
    """
    获取长于100楼的帖子
    :param path: save file path
    :param topic: shuiyuan topic id
    :param cookie_string: raw cookie string, get by read_cookie()
    :return: saved filename
    """
    topic = topic[1:]
    headers = {
        'User-Agent': UserAgentStr,
        'Cookie': cookie_string
    }
    url_topic = Shuiyuan_Topic + topic
    url_cooked = Shuiyuan_PostByNum + topic + '.json'
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
        url_raw = Shuiyuan_Raw + topic + '/' + str(i)
        response_raw = make_request(param=ReqParam(url_raw, headers), once=False)
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
    match_replace(path=path, filename=filename, topic=(topic[1:] if topic[0] == "L" else topic))
    print(f'编号为 #{topic[1:] if topic[0] == "L" else topic} 的帖子已备份为本地文件：{filename}\n')
    return True

def cookie_set():
    """
    设置cookie
    """
    while True:
        cookies = input('请输入cookie:(如果使用上次结果请输入"!!!",退出输入"???")\n')
        if cookies == "???":
            return None
        if cookies == "!!!":
            cookie_string = read_cookie()
            if len(cookie_string) != 0:
                set_cookie(data=cookie_string)
                break
            print('您还未设置cookie！')

def run():
    cookie_set()
    cookie_string = read_cookie()
    export(cookie_string)
if __name__ == "__main__":
    run()

