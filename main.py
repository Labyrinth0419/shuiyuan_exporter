from bs4 import BeautifulSoup
from image_handler import *
from attachments_handler import *
from constant import *
from utils import *
from typing import Tuple
from pathlib import Path
import argparse
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
    filename = topic + ' ' + filename
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
    # url_cooked = Shuiyuan_PostByNum + topic + '.json'
    param = ReqParam(url=url_topic, headers=headers)
    response_topic = make_request(param=param, once=False)
    url_json = url_topic + ".json"
    response_json = make_request(param=ReqParam(url=url_json, headers=headers), once=False)
    title = 'Empty'
    posts_count = 0
    if response_topic.status_code == 200 and response_topic.status_code == 200:
        content_topic = response_topic.text
        soup = BeautifulSoup(content_topic, 'html.parser')
        title = soup.title.string if soup.title else 'Empty'

        data = json.loads(response_json.text)
        posts_count = data['posts_count']

    filename = (str(title) + '.md').replace('/', ' or ')
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    filename = topic + ' ' + filename
    with open(path + filename, 'w', encoding='utf-8') as file:
        file.write("")

    # handle_futures = []
    @parallel_topic(topic=topic)
    def handle_func(layer_no: int)->Tuple[int,str]:
        url_raw = Shuiyuan_Raw + topic + '/' + str(layer_no)
        response_raw = make_request(param=ReqParam(url_raw, headers), once=False)
        if layer_no % 50 == 0:
            print(filename + ": post #" + str(layer_no) + " successfully saved!")
        if response_raw.status_code == 200:
            return layer_no, f'post #{layer_no}\n' + response_raw.text + "\n\n-----------------------------------\n\n"
        return layer_no, ""

    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     for i in range(1, posts_count + 1):
    #         handle_futures.append(executor.submit(handle_func, i))
    handle_res = handle_func()
    # join
    to_write:List[Tuple[int, str]] = []
    # for future in concurrent.futures.as_completed(handle_futures):
    #     to_write.append(future.result())
    for result in handle_res:
        to_write.append(result)
    to_write.sort(key=lambda x: x[0])
    file_text = "\n".join([x[1] for x in to_write])

    with open(path + filename, 'w', encoding='utf-8') as file:
        file.write(file_text)
    return filename

def export_exec(cookie_string:str, topic:str, is_long:bool):
    print(f'topic:{topic} 文字备份中...')
    topic = str(topic)
    print(topic)
    path = './posts/' + (topic[1:] if topic[0] == 'L' else topic) + '/'
    os.makedirs(path, exist_ok=True)
    if is_long:
        filename = long_post(path=path, topic=topic, cookie_string=cookie_string)
    else:
        filename = short_post(path=path, topic=topic, cookie_string=cookie_string)
    img_replace(path=path, filename=filename, topic=(topic[1:] if topic[0] == "L" else topic))
    match_replace(path=path, filename=filename, topic=(topic[1:] if topic[0] == "L" else topic))
    print(f'编号为 #{topic[1:] if topic[0] == "L" else topic} 的帖子已备份为本地文件：{filename}\n')
    print("Exit.")

def export_input(cookie_string:str):
    topic = input('请输入帖子编号:(退出请输入"???", 多于100楼的帖子请输入"L+帖子编号")\n')
    if topic == "???":
        raise Exception("Exit.")
    topic = str(topic)
    is_long = (topic[0] == 'L')
    export_exec(cookie_string, topic, is_long)


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
        if len(cookies) != 0:
            set_cookie(data=cookies)
            print("已同步新cookie到文件")
            break


def run(batch_topic:Tuple[str] = None):
    cookie_set()
    cookie_string = read_cookie()
    if batch_topic and len(batch_topic) != 0:
        for topic in batch_topic:
            try:
                export_exec(cookie_string=cookie_string, topic=topic, is_long=(topic[0]=='L'))
            except Exception as e:
                print(e)
        return
    else:
        while True:
            try:
                export_input(cookie_string=cookie_string)
            except Exception as e:
                print(e)
                break
def clean():
    directory = Path("./posts")
    for item in directory.iterdir():
        if item.is_dir() and re.match(r'\d+', item.name):
            print(f"目录: {item}")
            for file in item.iterdir():
                if file.name.endswith('Empty.md') or file.name.endswith('Single Sign On.md'):
                    os.remove(file)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The script is created to export posts on Shuiyuan Forum as markdown documents.")
    parser.add_argument('-b', '--batch', nargs='+',type=str, help='For test and CI: -b 1 2 3 means download the topic 1, 2, 3')
    parser.add_argument('-c', '--clean', action='store_true', help='clean the posts folder for possible meaningless md')

    args = parser.parse_args()
    if args.batch:
        print(args.batch)
        run(args.batch)
    elif args.clean:
        clean()
    else:
        run()

