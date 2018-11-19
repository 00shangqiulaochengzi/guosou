import os
import requests
import json
import hashlib
from multiprocessing import Pool
import threadpool


GET_KEY_PATH = 'D:/chenyan/爬虫关键字/国搜.txt'
SAVE_PIC_PATH = 'D:/chenyan/图片下载/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
}


# 获取文件夹中关键字
def get_keyword():
    if os.path.exists(GET_KEY_PATH):
        with open(GET_KEY_PATH, 'r') as f:
            keywords = f.readlines()
    else:
        print('文件夹不存在')
    return keywords


def get_url(keyword):
    datas = []
    url = 'http://image.chinaso.com/getpic?'
    for pag_num in range(1, 4):
        data = {
            "rn": "72",
            "st": str(pag_num * 72),
            "q": keyword
        }
        response = requests.get(url, params=data, headers=headers)
        results = json.loads(response.text)
        img_url = results['arrResults']
        for i in img_url:
            datas.append(([keyword, i['url']], None))
        pool_1 = threadpool.ThreadPool(2)
        reqs = threadpool.makeRequests(download, [im for im in datas])
        [pool_1.putRequest(req) for req in reqs]
        pool_1.wait()


def download(keyword, url):
    folder = GET_KEY_PATH.split('/')[-1].split('.')[0]
    if not os.path.exists(SAVE_PIC_PATH + folder):
        os.mkdir(SAVE_PIC_PATH + folder)
    if not os.path.exists(SAVE_PIC_PATH + folder + '/' + keyword):
        os.mkdir(SAVE_PIC_PATH + folder + '/' + keyword)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            m = hashlib.md5()
            m.update(response.content)
            file_md5 = m.hexdigest()
            if not os.path.exists(SAVE_PIC_PATH + folder + '/' + keyword + '/' + file_md5 + '.jpg'):
                with open(SAVE_PIC_PATH + folder + '/' + keyword + '/' + file_md5 + '.jpg', 'wb') as f:
                    f.write(response.content)
                    print(keyword, '--------->>', file_md5, '--------->>', '图片下载成功')
            else:
                print(keyword, '---------->>', '文件已经存在')
    except Exception as e:
        pass


if __name__ == '__main__':
    # get_url('鹿')
    keywords = get_keyword()
    pool = Pool(2)
    for keyword in keywords:
        keyword = keyword.strip()
        pool.apply_async(get_url, (keyword,))
    pool.close()
    pool.join()