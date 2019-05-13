from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import codecs
import json
import re


def get_page(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome()
        driver.get(url)
        return driver.page_source
    except:
        get_page(url)
        print(url)

def parse_page(html):
    pattern = re.compile(r'"frontImg":"(.*?)","title":"(.*?)","avgScore":(.*?),"allCommentNum":'
                         + r'(.*?),"address":"(.*?)","avgPrice":(.*?),"dealList":', re.S)
    try:
        items = re.findall(pattern, html)
    except:
        items = re.findall(pattern, str(html))
    for item in items:
        yield {
            'frontImg': item[0],
            'title': item[1],
            'allCommentNum': item[2],
            'adress': item[3],
            'avgPrice': item[4]
        }

def write_data(data):
    file = codecs.open('data.json', 'a', encoding='utf8')
    lines = json.dumps(dict(data), ensure_ascii=False) + '\n'
    file.write(lines)
    file.close()

def main():
    for i in range(1, 68):
        url = 'https://hz.meituan.com/meishi/pn{}/'.format(i)
        html = get_page(url)
        for data in parse_page(html):
            write_data(data)

if __name__ == '__main__':
    main()