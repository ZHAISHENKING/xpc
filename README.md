# django项目



运行项目

```bash
# 1.安装依赖
pip install -r requirements
# 2.启动项目,默认启动8000端口
python manage.py runserver
```



目录结构

```
.
├── LICENSE
├── README.md
├── db.sqlite3
├── manage.py
├── requirements.txt
├── templates
├── web
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-36.pyc
│   │   ├── models.cpython-36.pyc
│   │   ├── settings.cpython-36.pyc
│   │   ├── urls.cpython-36.pyc
│   │   └── wsgi.cpython-36.pyc
│   ├── cpsettings.py
│   ├── models.py
│   ├── settings.py
│   ├── templates
│   │   ├── comments.html
│   │   ├── homepage.html
│   │   ├── oneuser.html
│   │   ├── post.html
│   │   └── post_list.html
│   ├── urls.py
│   ├── views
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── composer.py
│   │   └── post.py
│   └── wsgi.py
└── xpc
    ├── __init__.py
    ├── scrapy.cfg
    └── xpc
        ├── __init__.py
        ├── __pycache__
        ├── cppipelines.py
        ├── cpsettings.py
        ├── db.sql
        ├── items.py
        ├── middlewares.py
        ├── pipelines.py
        ├── settings.py
        └── spiders

```



**因为涉及密码，我把所有需要密码的文件都只上传了副本，文件名前面带`cp`的**



django项目的展示依赖于数据库数据，需要您先运行scrapy爬虫



所用到的库

supervisor

pymysql

redis

django

Scrapy