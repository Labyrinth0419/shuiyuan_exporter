# shuiyuan_exporter

The reposity is created to export posts on Shuiyuan Forum as markdown documents.

### Prerequisites:

- Python 3.4+ (Now tested for 3.12 only)
- BeautifulSoup 4
- requests
- simple_term_menu

### Install dependencies:

```
pip install -r requirements.txt
```
Go to the SJTU shuiyuan site and get your cookies, then copy them to the `cookies.txt` file.

### Quick Start:

```
python main.py
```
Input `!!!` to confirm your cookies, and then input the topic ID you want to export. The script will download all the posts in the topic and export them as markdown documents.

e.g. `https://shuiyuan.sjtu.edu.cn/t/topic/75214`

```shell
$ python main.py
请输入cookie:(如果使用上次结果请输入"!!!",退出输入"???")

!!!

请输入帖子编号:(退出请输入"???")

75214

文字备份中...
......
图片载入中...
......
文件替换中...
.......
编号为 75214 的帖子已备份为本地文件：XXX.md(对应的图片在image文件夹)
```

### Other Details:
- we use threadingpool to fetch data concurrently
- you can use `python main.py --help` to **get more information about optional arguments**(like clean, batch, list etc)
- for developer, main.py -s and test.py might be helpful

### FAQ:

- Q: Why does the script need cookies?
- A: The script needs cookies to access the Shuiyuan Forum. Without cookies, the script cannot access the site and export the posts.

- Q: How to get the cookies?
- A: F12 in Shuiyuan Forum, find something like `{;}` in `network` tab. Copy the value of `cookie` and paste it to the `cookies.txt` file.

- Q: Why does the script saved a file "SJTU Single Sign On.md"?
- A: Update your cookie, your cookies are expired. You can delete this by `python main.py --clean`

- Q: How fast it is?
- A: In latest version, to pull a topic with 3800 posts and 100M images cost 10s.

- Q: Will the request be too frequently to be banned?
- A: It might be. We have tried to reduce the number of requests by paging and caching, but it still has about `post number / 20 + image number` requests due to discourse's limitation. So you have to handle this when you use the script to export a large number of topics.

- Q: Why can't make cookie fetch simpler be given password and jaccount?
- A: We've considered this. However, the solution usually has to introduce some headless browser like selenium-chrome, which will make the dependencies much bigger

### To Contribute
Now we are looking forward to more optimizations on below domains. 
- [✔] Video and Audio support
- [ ] Add more options for users to customize the export
- [ ] Better Error Handling, especially banned by the server
- [ ] Better Log system, `-v` and `-VV`
If you have some ideas, feel free to change the source code and contact us!


