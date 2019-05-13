import requests
import json
import re
from urllib.parse import urlencode
from requests.exceptions import RequestException

def get_page_index(offset, keyword):
    data = {
        'aid': '24',
        'app_name': 'web_search',
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'en_qc': '1',
        'cur_tab': '1',
        'from': 'search_tab',
        'pd': 'synthesis',
        'timestamp': '1556009459004'
    }
    url = 'https://www.toutiao.com/api/search/content/?' + urlencode(data)
    kv = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=kv)
        r.encoding = r.apparent_encoding
        if r.status_code == 200:
            return r.text
    except RequestException:
        print('请求索引页出错')

def parse_page_index(html):
    pattren = re.compile(r'"article_url":"(.*?)",', re.S)
    items = re.findall(pattren, html)
    for item in items:
        yield item

def get_page_detail(url):
    try:
        kv = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=kv)
        r.encoding = r.apparent_encoding
        if r.status_code == 200:
            return r.text
    except RequestException:
        print('请求详情页出错', url)

def parse_page_detail(html):
    pattern = re.compile('title: \'(.*?)\',', re.S)
    pattern1 = re.compile('src&#x3D;&quot;(.*?)&quot;', re.S)
    items = re.findall(pattern, html)
    items1 = re.findall(pattern1, html)
    return items + items1

def main():
    for i in range(100):
        html = get_page_index(20*i, '街拍')
        for item in parse_page_index(html):
            text = get_page_detail(item)
            data = parse_page_detail(text)
            print(data)
            if len(data) >= 2:
                for item in data:
                    with open('data.json', 'a', encoding='utf8') as f:
                        f.write(json.dumps(item, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()


