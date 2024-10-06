from bs4 import BeautifulSoup
from image_handler import *
from attachments_handler import *
from constant import *
from utils import *
from typing import Tuple
from pathlib import Path
import argparse
import pstats
from pstats import SortKey
import cProfile


def raw_post(path:str, topic:str)->str:
    """
    获取任意编号下的帖子
    """
    url_json = Shuiyuan_Topic_Json + topic + ".json"
    response_json = make_request(param=ReqParam(url_json), once=False)
    title = "Empty"
    if response_json.status_code == 200:
        data = json.loads(response_json.text)
        title = data['title']
    filename = (str(title) + '.md').replace('/', ' or ')
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    filename = topic + ' ' + filename
    with open(path + filename, 'w', encoding='utf-8') as file:
        file.write("")
    @parallel_topic_in_page(topic=topic, limit=raw_limit)
    def handle_func(page_no: int) -> Tuple[int, str]:
        url_raw = Shuiyuan_Raw + topic + '?page=' + str(page_no)
        response_raw = make_request(param=ReqParam(url_raw), once=False)
        if response_raw.status_code == 200:
            return page_no, code_block_fix(response_raw.text)
        return page_no, ""

    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     for i in range(1, posts_count + 1):
    #         handle_futures.append(executor.submit(handle_func, i))
    handle_res = handle_func()
    # join
    to_write: List[Tuple[int, str]] = []
    # for future in concurrent.futures.as_completed(handle_futures):
    #     to_write.append(future.result())
    for result in handle_res:
        to_write.append(result)
    to_write.sort(key=lambda x: x[0])
    file_text = "\n".join([x[1] for x in to_write])

    with open(path + filename, 'w', encoding='utf-8') as file:
        file.write(file_text)
    return filename

def export_exec(topic:str):
    topic = str(topic)
    topic = topic[1:] if topic[0] == "L" else topic # 兼容老API的 L123456
    print(f'topic:{topic} 文字备份中...')

    path = f'./posts/{topic}/'
    os.makedirs(path, exist_ok=True)
    last_time = time.time()
    filename = raw_post(path=path, topic=topic)
    print(f"文字爬取耗时: {time.time() - last_time} 秒")
    last_time = time.time()
    img_replace(path=path, filename=filename, topic=topic)
    print(f"图片爬取耗时: {time.time() - last_time} 秒")
    last_time = time.time()
    match_replace(path=path, filename=filename, topic=topic)
    print(f"附件爬取耗时: {time.time() - last_time} 秒")
    print(f'编号为 #{topic} 的帖子已备份为本地文件：{filename}\n')
    print("Exit.")

def export_input():
    topic = input('请输入帖子编号:(退出请输入"???")\n')
    if topic == "???":
        raise Exception("Exit.")
    export_exec(topic)


def cookie_set():
    """
    设置cookie
    如成功设置则返回True，否则返回False退出
    """
    while True:
        cookies = input('请输入cookie:(如果使用上次结果请输入"!!!",退出输入"???")\n')
        if cookies == "???":
            return False
        if cookies == "!!!":
            cookie_string = read_cookie()
            if len(cookie_string) != 0:
                return True
            print('您还未设置cookie！')
        elif len(cookies) != 0:
            set_cookie(data=cookies)
            print("已同步新cookie到文件")
            return True


def run(batch_topic:Tuple[str] = None, ask_cookie=True):
    if ask_cookie:
        cookie_set()
    if batch_topic and len(batch_topic) != 0:
        for topic in batch_topic:
            try:
                export_exec(topic=topic)
            except Exception as e:
                print(e)
        return
    else:
        while True:
            try:
                export_input()
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

def stat(program: str):
    stat_dir = Path("./stat")
    if not stat_dir.exists():
        stat_dir.mkdir()
    cProfile.run(f'{program}', './stat/run_stats.txt')
    p = pstats.Stats('./stat/run_stats.txt')
    p.strip_dirs().sort_stats(SortKey.TIME).print_stats(10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The script is created to export posts on Shuiyuan Forum as markdown documents.")
    parser.add_argument('-b', '--batch', nargs='+',type=str, help='For test and CI: -b 1 2 3 means download the topic 1, 2, 3')
    parser.add_argument('-c', '--clean', action='store_true', help='clean the posts folder for possible meaningless md')
    parser.add_argument('-n','--not_ask_cookie', action='store_true', help='if ask for cookie or use saved cookie directly')
    parser.add_argument('-s', '--stat', action='store_true', help="stat the time consuming analysis and save.")
    args = parser.parse_args()
    ask = not args.not_ask_cookie if args.not_ask_cookie else True

    if args.batch:
        print(args.batch)
        run(args.batch, ask_cookie=ask)
    elif args.clean:
        clean()
    elif args.stat:
        stat("run(['276006'], False)")
    else:
        run(ask_cookie=ask)
