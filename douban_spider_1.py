#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""标题: 多进程 + 多线程爬取豆瓣读书多个分类下的书籍信息并以json格式保存

当前功能描述： 爬取 4 个分类（理财，中国文学，外国文学，历史）
下前 20 页的书籍信息（每页 20 本书，合计每个分类前 400 本书），
并在当前脚本目录下新建一个以“脚本名称命名“的文件夹来保存json
文件，json文件名以每个分类的名字命名

可扩展: 通过增加 type_url_prefixes 里的分类链接，
可以增加爬取的分类.

作者: Hunter-0x07
最初完成时间: 2020.12.03 15:57
"""

from multiprocessing import Process
import threading
import requests
import time
from lxml import etree
import os
from pathlib import Path
from urllib.parse import urlparse, unquote
import json
import logging


def get_html_p(type_prefix):
    """为每个进程创建新的线程
    param: type_prefix 每个分类页面前缀 https://book.douban.com/tag/%E7%90%86%E8%B4%A2
    return: None
    """
    # 列表用于保存已创建的线程
    t_list = []
    
    for start_page in range(20):
        # 单个页面的 url https://book.douban.com/tag/%E7%90%86%E8%B4%A2?start=200
        page_url = f"{type_prefix}?{start_page*20}"

        # 单个进程下开启多个线程爬取每个页面
        t = threading.Thread(target=get_html_t, args=(page_url, ))
        t.start()
        logging.info(f"创建新线程: {t.name}")
    
    # 阻塞，等待完成
    for t in t_list:
        t.join()

def get_html_t(page_url):
    """获取单个分类下的单个页面
    param: page_url 单个页面的 url https://book.douban.com/tag/%E7%90%86%E8%B4%A2?start=200
    return: None
    """
    # 构造请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Referer': 'https://book.douban.com/',
    }

    # 发起请求
    try:
        type_page_response = requests.get(page_url, headers=headers)
    except Exception as e:
        logging.error(f"出现错误: {e}")

    # 处理获得单个分类下所有书籍
    selector = etree.HTML(type_page_response.text)
    
    # 获取书籍名称，链接，评分，简要描述
    titles = selector.xpath('//ul[@class="subject-list"]//div[@class="info"]//a/@title')
    hrefs = selector.xpath('//ul[@class="subject-list"]//div[@class="info"]//a/@href')
    scores = selector.xpath('//ul[@class="subject-list"]//span[@class="rating_nums"]/text()')
    descriptions = selector.xpath('//ul[@class="subject-list"]//p/text()')

    # 将每本书信息放入元组并合并为列表
    book_list = list(zip(titles, hrefs, scores, descriptions))

    # 获取分类名称做 json 文件前缀，例: 小说.json
    o = unquote(urlparse(page_url).path)
    file_stem = o.split("/")[2]
    file_suffix = '.json'
    file_name = file_stem + file_suffix

    # 将结果保存到json文件
    save_json(book_list, file_name)

def save_json(book_list, file_name):
    """将不同分类以json格式保存
    param: book_list 书籍列表 [(书籍名称, 书籍链接, 豆瓣评分, 内容简介), (...)]
    return: None
    """
    p = Path(__file__)

    # 声明保存 json 文件的目录的绝对路径，
    # 格式为 "当前脚本所在目录+当前脚本名称"
    file_dir = os.path.join(p.parent, p.stem)
    
    if not os.path.isdir(file_dir):
        os.mkdir(file_dir)
    
    # 构造 json 文件的绝对路径
    file_abs = os.path.join(file_dir, file_name)
    
    try:
        # 将结果以 json 格式保存，格式为 "分类名称.json"
        with open(file_abs, 'a+') as f:
            json.dump(book_list, f, ensure_ascii=False)
    except FileNotFoundError as e:
        logging.error(f"权限不够, 无法创建文件: {e}")
    except IOError as e:
        logging.error(f"写入文件出错: {e}")
    except Exception as e:
        logging.error(f"其他出错: {e}")



def main():
    """ Entrance of program """
    # 配置日志选项
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
    )

    # 4 个书籍分类的 url 链接
    type_url_prefixes = [
        # 理财 例: https://book.douban.com/tag/理财
        "https://book.douban.com/tag/%E7%90%86%E8%B4%A2",
        # 中国文学
        "https://book.douban.com/tag/%E4%B8%AD%E5%9B%BD%E6%96%87%E5%AD%A6",
        # 外国文学
        "https://book.douban.com/tag/%E5%A4%96%E5%9B%BD%E6%96%87%E5%AD%A6",
        # 历史
        "https://book.douban.com/tag/%E5%8E%86%E5%8F%B2",
    ]

    # 列表用于保存创建的进程
    p_list = []

    # 开始时间
    start_time = time.time()

    # 开启多个进程爬取分类下所有书籍的链接
    for type_prefix in type_url_prefixes:
        p = Process(target=get_html_p, args=(type_prefix, ))
        p.start()
        logging.info(f"创建新进程, 进程PID为: {p.pid}")
        p_list.append(p)

    # 阻塞所有进程，让主程序等待进程执行完毕
    for p in p_list:
        p.join()

    # 执行完成花费时间
    print(f"Spending time: {time.time() - start_time}")


if __name__ == "__main__":
    main()
    # f_abs = __file__
    # curr_dir = os.path.dirname(f_abs)
    # p = Path(__file__)
    # file_stem = p.stem
    # target_json = os.path.join(curr_dir, file_stem, )
    # print(p.parent)
    # # if not os.path.exists(curr_dir.join(file_name))
    # 当前执行文件绝对路径
    # p = Path(__file__)

    # # 目标目录名称
    # target_dir = os.path.join(p.parent, p.stem)
    
    # # 创建需要的目录
    # if not os.path.isdir(target_dir):
    #     os.mkdir(target_dir)
    # str_1 = "https://book.douban.com/tag/%E5%A4%96%E5%9B%BD%E6%96%87%E5%AD%A6"
    # print(str_1)