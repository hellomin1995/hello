import requests
import re
import json
import pymongo
from requests.exceptions import RequestException
from multiprocessing import Pool
# from maoyantop100.config import *

MONGO_URL = 'localhost'
MONGO_DB = 'maoyan'
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def get_one_page(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.text
        return None
    except RequestException:
        return None

def parse_one_page(html):
    pattern = re.compile('<dd>.*?<i class="board-index.*?">(\d+)</i>.*?<img data-src="(.*?)".*?<a href="/films/.*?">(.*?)</a>.*?<p class="star">(.*?)</p>.*?<p class="releasetime">(.*?)</p>.*?<i class="integer">(.*?)</i><i class="fraction">(.*?)</i>.*?</dd>', re.S)
    items = re.findall(pattern, html)
    for item in items:
        yield {
            'index': item[0],
            'image': item[1],
            'title': item[2],
            'actor': item[3].strip()[3:],
            'time': item[4].strip()[5:],
            'score': item[5] + item[6]
        }

def write_to_file(content):
    with open('result.json', 'a', encoding='utf8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')

def save_mongo(result):
    MONGO_TABLE = 'maoyan'
    if db[MONGO_TABLE].insert(result):
        print('ok', result)
        return True
    return False

def main(offset):
    url = 'http://maoyan.com/board/4?offset=' + str(offset)
    html = get_one_page(url)
    parse_one_page(html)
    for item in parse_one_page(html):
        # save_mongo(item)
        write_to_file(item)

if __name__ == '__main__':
    # for i in range(10):
    #     main(i*10)
    pool = Pool()
    pool.map(main, [i*10 for i in range(10)])