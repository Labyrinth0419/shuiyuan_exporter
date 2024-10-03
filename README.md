# shuiyuan_exporter

The reposity is created to export posts on Shuiyuan Forum as markdown documents.

prerequisites:

- Python 3.4+ (Now tested for 3.12 only)
- BeautifulSoup 4
- requests

install dependencies:

```
pip install -r requirements.txt
```
Go to the SJTU shuiyuan site and get your cookies, then copy them to the `cookies.txt` file.

Quick Start:

```
python main.py
```
Input `!!!` to confirm your cookies, and then input the topic ID you want to export. The script will download all the posts in the topic and export them as markdown documents.

e.g. `https://shuiyuan.sjtu.edu.cn/t/topic/75214`

```shell
$ python main.py
请输入cookie:(如果使用上次结果请输入"!!!",退出输入"???")

!!!

请输入帖子编号:(退出请输入"???", 多于100楼的帖子请输入"L+帖子编号")

75214

文字备份中...
图片载入中...
文件替换中...
编号为 75214 的帖子已备份为本地文件：XXX.md
```

Other Details:
- we use threadingpool to fetch data concurrently
- you can use `python main.py --help` to get more information about optional arguments


FAQ:

- Q: Why does the script need cookies?
- A: The script needs cookies to access the Shuiyuan Forum. Without cookies, the script cannot access the site and export the posts.

- Q: How to get the cookies?
- A: F12 in Shuiyuan Forum, find something like `{;}` in `network` tab. Copy the value of `cookie` and paste it to the `cookies.txt` file.

- Q: Why does the script saved a file "SJTU Single Sign On.md"?
- A: Update your cookie, your cookies are expired.

