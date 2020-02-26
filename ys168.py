#!/usr/bin/python

import requests
from tqdm import tqdm
import sys
import re
import os

def download_file(url,save_path=None):
    if not save_path:
        save_path = url[url.rfind('/')+1:]
    r = requests.get(url, stream=True)
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024*16
    t=tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(save_path, 'wb') as f:
        for data in r.iter_content(block_size):
            t.update(len(data))
            f.write(data)
    t.close()
    if total_size != 0 and t.n != total_size:
        print("download error")


def process(index_url):
    username = re.findall('//(.+?)\.ys168.com',index_url)[0]
    if not os.path.exists(username):
        os.mkdir(username)
    os.chdir(username)
    dir_url = 'http://cd.ys168.com/f_ht/ajcx/ml.aspx?cz=ml_dq&_dlmc=%s&_dlmm='%(username)
    dir_text = requests.get(dir_url).text
    dir_data = re.findall('<li id="ml_(\d+?)" class="gml">.+?<a class="ml" href="javascript:;">(.+?)</a>.+?</ul></li>',dir_text,re.DOTALL)
    # print(dir_data)
    for (dir_id,dir_name) in dir_data:
        print("[ %s ]"%(dir_name))
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        os.chdir(dir_name)
        file_list_url = "http://cd.ys168.com/f_ht/ajcx/wj.aspx?cz=dq&mlbh=%s&_dlmc=%s&_dlmm="%(dir_id,username)
        file_list_text = requests.get(file_list_url).text
        file_list_data = re.findall('<li id=.+?>.+?<a href="(.+?)".+?>(.+?)</a>.+?</li>',file_list_text,re.DOTALL)
        # print(file_list_data)
        for (file_url,file_name) in file_list_data:
            print(">>>> %s"%(file_name))
            download_file(file_url,file_name)
        os.chdir("..")

if __name__ == '__main__':
    process(sys.argv[1])