#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""标题: 多线程抓取知乎任意话题排名前400条的答案内容

步骤: 
(1) 构建json接口列表
----通过for loop构造接口链接，因为接口每次返回10条数据，
所以400条数据只需要循环40次，构造40条链接即可

(2) 遍历json接口获取数据
----构造headers头
----发送GET请求获取响应

(3) 提取所需内容并保存
----提取问题和对应的答案内容
----在当前脚本文件所在目录以json文件格式保存数据，json文件
保存以当前脚本名称作为json文件名.

作者: Hunter-0x07
版本: 1.5 

改进: 单线程改为多线程，增加异常处理机制和日志功能.
运行时间: 17秒，较单线程速度提升了40秒
"""

import requests
from pathlib import Path
import os
import json
import time
import threading
import logging


def build_json_url() -> list:
    """构建json接口列表"""
    json_url_list = []

    for i in range(40):
        json_url = f"https://www.zhihu.com/api/v4/topics/19552832/feeds/essence?include=data[%3F(target.type%3Dtopic_sticky_module)].target.data[%3F(target.type%3Danswer)].target.content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata[%3F(target.type%3Dtopic_sticky_module)].target.data[%3F(target.type%3Danswer)].target.is_normal%2Ccomment_count%2Cvoteup_count%2Ccontent%2Crelevant_info%2Cexcerpt.author.badge[%3F(type%3Dbest_answerer)].topics%3Bdata[%3F(target.type%3Dtopic_sticky_module)].target.data[%3F(target.type%3Darticle)].target.content%2Cvoteup_count%2Ccomment_count%2Cvoting%2Cauthor.badge[%3F(type%3Dbest_answerer)].topics%3Bdata[%3F(target.type%3Dtopic_sticky_module)].target.data[%3F(target.type%3Dpeople)].target.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge[%3F(type%3Dbest_answerer)].topics%3Bdata[%3F(target.type%3Danswer)].target.annotation_detail%2Ccontent%2Chermes_label%2Cis_labeled%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Canswer_type%3Bdata[%3F(target.type%3Danswer)].target.author.badge[%3F(type%3Dbest_answerer)].topics%3Bdata[%3F(target.type%3Danswer)].target.paid_info%3Bdata[%3F(target.type%3Darticle)].target.annotation_detail%2Ccontent%2Chermes_label%2Cis_labeled%2Cauthor.badge[%3F(type%3Dbest_answerer)].topics%3Bdata[%3F(target.type%3Dquestion)].target.annotation_detail%2Ccomment_count%3B&limit=10&offset={i*10}"
        json_url_list.append(json_url)

    return json_url_list


def get_data(url: str) -> None:
    """遍历json接口获取数据
    param: json接口url
    return: None
    """
    # 构造headers头
    cookie = '_zap=a2e18207-8e5e-4bdf-817a-4b3f9a6b80c9; d_c0="ALCWIdUPShKPTubFWbqWOvMLw_V1N35WT2g=|1606987851"; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1606987868; capsion_ticket="2|1:0|10:1606992331|14:capsion_ticket|44:MGJmYWMyZmM2ZWJlNDNlYmI5M2NlNWU1ZThjZWFhMjc=|66651c7a039f77e12a7f3c4fd00d628c0efe30e1948242160db39dc16cd075ce"; z_c0="2|1:0|10:1606992346|4:z_c0|92:Mi4xOU5ONkF3QUFBQUFBc0pZaDFROUtFaVlBQUFCZ0FsVk4yZy0yWUFDUTlSNE1lRVpwNEtLVWI5eVRXNFpGek53WmtR|0dbafd07561b8a826081a4ac60407f350e741c625f22fafd548ab3fdb79e9b5c"; tst=h; tshl=; q_c1=e95eadae16904ca1be3c7369b3e93be5|1606994198000|1606994198000; KLBRSID=81978cf28cf03c58e07f705c156aa833|1607040356|1607040351; _xsrf=8ff08ac5-98d2-4dc9-af68-cc58dd1582ed; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1607040372'
    user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0"
    referer = "https://www.zhihu.com/topic/19552832/top-answers"
    connection = "keep-alive"

    headers = {
        "Cookie": cookie,
        "User-Agent": user_agent,
        "Referer": referer,
        "Connection": connection,
    }

    # 发送GET请求获取响应
    try:
        res = requests.get(url=url, headers=headers)
    except Exception as e:
        logging.error(f"请求发生错误: {e}")

    answers = res.json()['data']

    # 话题问题与相应答案组成的字典 {question: answer, ...}
    data_dict = {}

    for answer in answers:
        # 个别json数据没有和总体结构一样，这里增加异常处理来避免掉
        try:
            question = answer["target"]["question"]["title"]
            content = answer["target"]["content"]
            data_dict[question] = content

        except Exception:
            logging.warning(f"个别json数据没有和总体结构一样")

    # 保存数据
    save_data(data_dict)


def save_data(data_dict: dict) -> None:
    """将内容以json文件保存，并以当前脚本名命名
    param: 话题问题与相应答案组成的字典 {question: answer, ...}
    return: None
    """
    p = Path(__file__)

    # 构造json文件绝对路径
    file_suffix = '.json'
    file_path = os.path.join(p.parent, p.stem)
    file_abs = file_path + file_suffix
    try:
        with open(file_abs, "a+") as f:
            json.dump(data_dict, f, ensure_ascii=False)
    except FileNotFoundError as e:
        logging.error(f"权限不够, 无法创建文件: {e}")
    except IOError as e:
        logging.error(f"写入文件出错: {e}")
    except Exception as e:
        logging.error(f"其他错误: {e}")


def main():
    """本程序入口函数"""
    # 配置日志选项
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
    )

    # 记录程序开始运行时间
    start_time = time.time()
    logging.info(f"程序启动")

    # 构建json接口列表
    json_url_list = build_json_url()

    # 创建列表保存已创建的线程
    thread_list = []

    # 遍历json接口获取数据
    for url in json_url_list:
        # 创建并开启线程
        t = threading.Thread(target=get_data, args=(url, ))
        t.start()
        logging.info(f"创建并启动新线程: {t.name}")
        thread_list.append(t)

    # 阻塞，让主程序等待全部线程完成
    for t in thread_list:
        t.join()

    logging.info(f"运行花费时间: {time.time()-start_time}")


if __name__ == "__main__":
    main()
    # url = "https://www.zhihu.com/api/v4/topics/19552832/feeds/essence?include=data[%3F(target.type%3Dtopic_sticky_module)].target.data[%3F(target.type%3Danswer)].target.content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata[%3F(target.type%3Dtopic_sticky_module)].target.data[%3F(target.type%3Danswer)].target.is_normal%2Ccomment_count%2Cvoteup_count%2Ccontent%2Crelevant_info%2Cexcerpt.author.badge[%3F(type%3Dbest_answerer)].topics%3Bdata[%3F(target.type%3Dtopic_sticky_module)].target.data[%3F(target.type%3Darticle)].target.content%2Cvoteup_count%2Ccomment_count%2Cvoting%2Cauthor.badge[%3F(type%3Dbest_answerer)].topics%3Bdata[%3F(target.type%3Dtopic_sticky_module)].target.data[%3F(target.type%3Dpeople)].target.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge[%3F(type%3Dbest_answerer)].topics%3Bdata[%3F(target.type%3Danswer)].target.annotation_detail%2Ccontent%2Chermes_label%2Cis_labeled%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Canswer_type%3Bdata[%3F(target.type%3Danswer)].target.author.badge[%3F(type%3Dbest_answerer)].topics%3Bdata[%3F(target.type%3Danswer)].target.paid_info%3Bdata[%3F(target.type%3Darticle)].target.annotation_detail%2Ccontent%2Chermes_label%2Cis_labeled%2Cauthor.badge[%3F(type%3Dbest_answerer)].topics%3Bdata[%3F(target.type%3Dquestion)].target.annotation_detail%2Ccomment_count%3B&limit=10&offset=0"
    # get_data(url)
    # p = Path(__file__)
    # print(os.path.join(p.parent, p.stem))
