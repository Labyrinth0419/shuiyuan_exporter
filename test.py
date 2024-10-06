import subprocess
import re
import sys
import argparse
from typing import List, Dict

# 命令和次数
_test_output = """
topic:276006 文字备份中...
总页数 37: 正在爬取......
工作已加载完毕
--- 已完成工作: 0/37
--- 已完成工作: 10/37
--- 已完成工作: 20/37
--- 已完成工作: 30/37
文字爬取耗时: 0.9550602436065674 秒
图片载入中...
总页数 181: 正在爬取......
工作已加载完毕
--- 已完成工作: 0/181
--- 已完成工作: 10/181
--- 已完成工作: 20/181
--- 已完成工作: 30/181
--- 已完成工作: 40/181
--- 已完成工作: 50/181
--- 已完成工作: 60/181
--- 已完成工作: 70/181
--- 已完成工作: 80/181
--- 已完成工作: 90/181
--- 已完成工作: 100/181
--- 已完成工作: 110/181
--- 已完成工作: 120/181
--- 已完成工作: 130/181
--- 已完成工作: 140/181
--- 已完成工作: 150/181
--- 已完成工作: 160/181
--- 已完成工作: 170/181
--- 已完成工作: 180/181
图片爬取耗时: 8.017342567443848 秒
文件替换中...
总页数 181: 正在爬取......
工作已加载完毕
--- 已完成工作: 0/181
--- 已完成工作: 10/181
--- 已完成工作: 20/181
--- 已完成工作: 30/181
--- 已完成工作: 40/181
--- 已完成工作: 50/181
--- 已完成工作: 60/181
--- 已完成工作: 70/181
--- 已完成工作: 80/181
--- 已完成工作: 90/181
--- 已完成工作: 100/181
--- 已完成工作: 110/181
--- 已完成工作: 120/181
--- 已完成工作: 130/181
--- 已完成工作: 140/181
--- 已完成工作: 150/181
--- 已完成工作: 160/181
--- 已完成工作: 170/181
--- 已完成工作: 180/181
附件爬取耗时: 0.41994595527648926 秒
"""

if __name__ == '__main__':
    command = ""
    n = 5
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number', help="repeat times to calculate the avg time consumption")
    parser.add_argument('-t', '--test', action='store_true', help="test this program")
    parser.add_argument('-c', '--command', type=str, help="command to execute")
    args = parser.parse_args()
    if args.number:
        n = int(args.number)
    if args.command:
        command = args.command
    # 用于存储每次运行的耗时
    times:Dict[str, List[float]] = {}

    # 运行命令 n 次
    for _ in range(n):
        if args.test:
            output = _test_output
        else:
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = result.stdout.decode('utf-8')
        match_lists = re.findall(r'([^\x00-\xff]+)爬取耗时: ([\d.]+) 秒', output)
        for match in match_lists:
            if match and len(match) >= 2:
                if not match[0]in times:
                    times[match[0]] = []
                times[match[0]].append(float(match[1]))

    # 计算平均耗时
    if times:
        averages = {}
        for item in times.keys():
            averages[item] = sum(times[item]) / len(times[item])
        print(f" {command} 在 {n} 次运行中的平均耗时:")
        # 输出 Markdown 表格
        print("| 爬取部分 | 时间 (秒) |")
        print("|---------|-----------------------|")
        for item in averages.keys():
            print(f"| {item} | {averages[item]:.3f} |")
    else:
        print("No valid time found.")