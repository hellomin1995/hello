from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# from multiprocessing.pool import Pool
# from xianyu.config import *
import re
import time
import random
import requests
import json
import logging
# import sys
# import pymongo
import os.path

# MONGO_URL = 'localhost'
# MONGO_DB = 'xianyu'
# client = pymongo.MongoClient(MONGO_URL)
# db = client[MONGO_DB]


def get_proxy():
    # 获取随机IP
    proxy = [
        "http://101.37.118.54:8888",
        "http://58.87.68.189:1080",
        "http://119.190.34.70:80",
        "http://111.40.84.73:9999",
        "http://101.251.215.232:8081",
        "http://117.191.11.79:80",
        "http://121.12.85.2:80",
        "http://47.97.106.71:80",
        "http://111.230.113.238:9999",
        "http://58.87.98.112:1080",

    ]
    proxies = {}
    proxies['http'] = proxy[random.randint(0, len(proxy) - 1)]
    print(proxies)
    return proxies

def get_page(url, proxies, num, i):
    # 获取首页html
    try:
        proxies = proxies['http']
        driver = webdriver.Chrome()
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--proxy-server=' + proxies)
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'body > div.main > div.tabbar-wrap > div:nth-child({0}) > p'.format(num + 4))))
        submit.click()
        if i > 0:
            for n in range(i):
                button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'body > div.main > div.pagination > div > button.btn-next > i')))
                button.click()
        time.sleep(2)
        text = driver.page_source
        driver.quit()
        return text
    except:
        # logging.error('{}首页请求出错'.format(url))
        print(logging.error('{}首页请求出错'.format(url)))
        proxies = get_proxy()
        get_page(url, proxies, num, i)


def parse_url(html):
    # 解析首页html，获取详情页面url
    pattern = re.compile(r'<a data-v-eab80fd8="" href="//(.*?)"', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield 'https://' + item

def get_dital_page(url, proxies):
    # 获取详情页面html
    try:
        kv = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=kv, proxies=proxies)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        print(logging.error('{}详情页出错！'.format(url)))
        return ''

def parse_dital_url(html):
    # 解析详情页面html，获取数据
    pattern = re.compile(r'<span class="para">原　　价：</span>.*?<span>(.*?)</span>', re.S)
    item = re.findall(pattern, html)
    if len(item) == 0:
        pattern = re.compile(
            r'class="hCard fn" target="_blank">(.*?)</a>.*?<h1 class="title">(.*?)</h1>.*?<span class="price big"><b>&yen;</b><em>(.*?)</em>.*?<em>(.*?)</em>.*?<em>(.*?)</em>.*?<span data-term="0" class="J_Term term">(.*?)</em>',
            re.S)
        items = re.findall(pattern, html)
        for item in items:
            yield {
                '卖家': item[0],
                '商品': item[1],
                '转卖价': item[2],
                '成色': item[3],
                '所在地': item[4],
                '交易方式': item[5]
            }
    else:
        pattern = re.compile(
            r'class="hCard fn" target="_blank">(.*?)</a>.*?<h1 class="title">(.*?)</h1>.*?<span class="price big"><b>&yen;</b><em>(.*?)</em>.*?<span class="para">原　　价：</span>.*?<span>(.*?)</span>.*?<em>(.*?)</em>.*?<em>(.*?)</em>.*?<span data-term="0" class="J_Term term">(.*?)</em>',
            re.S)
        items = re.findall(pattern, html)
        for item in items:
            yield {
                '卖家': item[0],
                '商品': item[1],
                '转卖价': item[2],
                '原价': item[3],
                '成色': item[4],
                '所在地': item[5],
                '交易方式': item[6]
            }

def chiose():
    # 选择需要爬取数据的类型
    print(' 手机 数码 租房 服装 居家 美妆 运动 家电 玩具乐器 ')
    lit = ['手机', '数码', '租房', '服装', '居家', '美妆', '运动', '家电', '玩具乐器']
    data = input('请输入选项：')
    # data = '居家'
    if data in lit:
        for i in range(0, len(lit)):
            if data == lit[i]:
                return i
    else:
        print(logging.error('选项不存在请重新输入选项!如( 手机 数码 租房 服装 居家 美妆 运动 家电 玩具乐器 )'))
        data = input('请重新输入选项：')
        if data in lit:
            for i in range(0, len(lit)):
                if data == lit[i]:
                    return i

def file_name(num):
    # 生成数据文件的名称
    lit = ['手机', '数码', '租房', '服装', '居家', '美妆', '运动', '家电', '玩具乐器']
    # datatime = time.strftime('%Y-%m-%d', time.localtime())
    # name = lit[num] + datatime + '.json'
    name = lit[num]
    print(name)
    return name

def write_to_file(item, filename):
    # 存储详情页面数据
    with open(filename + '.txt', 'a', encoding='utf8') as f:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

def write_url_to_file(item, filename):
    # 存储详情页面url
    with open(filename + '链接.json', 'a', encoding='utf8') as f:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

# def dital_url(html, filename):
#     # url去重
#     data = read_url(filename)
#     for i in parse_dital_page(html):
#         if i in data:
#             print('url已存在！')
#         else:
#             write_url_to_file(i)
#             return i

def read_url(filename):
    # 从文件中读取详情页面的链接
    data = set()
    if os.path.isfile(filename + '.json'):
        with open(filename + '链接.json', 'r', encoding='utf8') as f:
            for line in f:
                da = json.loads(line)
                yield da
                # data.add(da)
            # return data
    else:
        with open(filename + '.json', 'a', encoding='utf8') as f:
            f.writable()


# def save_mongo(item):
#     MONGO_TABLE = 'xianyu'
#     if db[MONGO_TABLE].insert(item):
#         print('ok', item)
#         return True
#     return False


def main():
    # logf = open("xianyu.log", "a+")
    # stderr = sys.stderr
    # stdout = sys.stdout
    # sys.stderr = logf
    # sys.stdout = logf
    # sys.stdout = stdout
    url = 'https://2.taobao.com/'
    num = chiose()
    filename = file_name(num)
    # dital_url_set = set()
    for i in range(2):
        print(i + 1)
        proxies = get_proxy()
        html = get_page(url, proxies, num, i)  #首页的html
        for dital_url in parse_url(html):
            data = set()
            for da in read_url(filename):
                data.add(da)
            if dital_url in data:
                print('url已存在！')
            else:
                dital_html = get_dital_page(dital_url, proxies)
                write_url_to_file(dital_url, filename)
                if dital_html != '':
                    for item in parse_dital_url(dital_html):
                        print(item)
                        write_to_file(item, filename)
    # logf.close()

if __name__ == '__main__':
    t0 = time.time()
    main()
    # t1 = time.time()
    # pool = Pool(10)
    # pool.map(main())
    t2 = time.time()
    print(t2 - t0)



