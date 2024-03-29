#!/usr/bin/python

import requests
from tqdm import tqdm
import sys
import re
import os

SUBDIR = "ys168_downloaded"

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cookie': '',
    'DNT': '1',
    'Host': 'cc.ys168.com',
    'Referer': 'http://cc.ys168.com/f_ht/ajcx/000ht.html?bbh=1139',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}

session = requests.Session()
session.headers = headers


def download_file(url, save_path=None, overwrite=False):
    if not save_path:
        save_path = url[url.rfind('/')+1:]
    if os.path.exists(save_path) and not overwrite:
        return
    r = session.get(url, stream=True)
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024*16
    t = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(save_path, 'wb') as f:
        for data in r.iter_content(block_size):
            t.update(len(data))
            f.write(data)
    t.close()
    if total_size != 0 and t.n != total_size:
        print("download error")


def process(index_url):
    username = re.findall('//(.+?)\.ys168.com', index_url)[0]
    if not os.path.exists(username):
        os.mkdir(username)
    os.chdir(username)

    # t = session.get(index_url).text
    # print(t)

    dir_url = 'http://cc.ys168.com/f_ht/ajcx/ml.aspx?cz=ml_dq&_dlmc=%s&_dlmm=' % (
        username)

    dir_text = session.get(dir_url).text
    # print(dir_text)
    dir_data = re.findall(
        '<li id="ml_(\d+?)" class="gml".+?<a class="ml" href="javascript:;">(.+?)</a>.+?</ul></li>', dir_text, re.DOTALL)
    print(dir_data)
    # return
    for (dir_id, dir_name) in dir_data:
        print("[ %s ]" % (dir_name))
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        os.chdir(dir_name)
        file_list_url = "http://cd.ys168.com/f_ht/ajcx/wj.aspx?cz=dq&mlbh=%s&_dlmc=%s&_dlmm=" % (
            dir_id, username)
        file_list_text = session.get(file_list_url).text
        file_list_data = re.findall(
            '<li id=.+?>.+?<a href="(.+?)".+?>(.+?)</a>.+?</li>', file_list_text, re.DOTALL)
        # print(file_list_data)
        for (file_url, file_name) in file_list_data:
            print(">>>> %s" % (file_name))
            try:
                download_file(file_url, file_name)
            except Exception as e:
                print(e)
        os.chdir("..")


if __name__ == '__main__':
    if not os.path.exists(SUBDIR):
        os.mkdir(SUBDIR)
    os.chdir(SUBDIR)
    process(sys.argv[1])
