# This repo is in Chinese, sorry ¯\_(ツ)_/¯
# 帮助你在成语接龙里逼死人的小工具
## Usage:
1. 按照自己需求在`discover_routes.py`里修改全局变量`MAX_DEPTH`和`TARGET_IDIOM`  
`MAX_DEPTH`是指从到达目标成语最高接龙数  
`TARGET_IDIOM`是目标成语
2. 配置MySql服务器
3. 运行脚本  
然后你的数据库里将会有所有接龙数据

你可以自行写sql语句使用 或者用这个repo里的web客户端

## Web端使用:
1. 安装`Flask`
2. 运行`app.py`
3. 浏览器里打开`http://localhost:5000`

## Credits
成语数据来自[**清华大学开放中文词库**](http://thuocl.thunlp.org/ "清华大学开放中文词库")