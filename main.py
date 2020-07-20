import json
import requests
import re
import time
import random
from tqdm import tqdm
import pandas as pd


def get_province_urls():
    r = requests.get('http://www.pharmnet.com.cn/search/template/yljg_index.htm')
    r.encoding = r.apparent_encoding
    html = r.text
    provinces = re.findall(re.compile('<a href="(.*p=1)">(.*?)</a>'), html)
    return provinces


def get_clinics_from_province_url(p_url):
    r = requests.get(p_url[0], timeout=5)
    r.encoding = r.apparent_encoding
    # print(r.encoding)
    html = r.text
    res = []
    pages = int(re.findall('记录,<font color="#FF0000">(.*)?</font>页,显示', html)[0])

    print('STARING GETTING {}...'.format(p_url[1]))
    for p in tqdm(range(pages)):
        # print(p)
        try:
            sub_url = p_url[0][:-1] + str(p + 1)
            rr = requests.get(sub_url, timeout=5)
            rr.encoding = rr.apparent_encoding
            sub_html = rr.text
            # print(sub_html)
            one_clinic_name = re.findall(r'<font color="#006600"><u>(.*)?<.u>', sub_html)
            one_clinic_address = re.findall(r'<td width="45%" align="left">(.*)?</td>', sub_html)
            one_clinic_mail_code = re.findall(r'<td width="25%" align="left">(\d*)</td>', sub_html)

            # one_clinic_contact = re.findall(r'<td align="left">(.*?)</td>\n<td align="right"></td>', sub_html)
            # one_clinic_bed_num = re.findall(r'<td align="right"></td>', sub_html)
            # print(one_clinic_name, one_clinic_address, one_clinic_mail_code)
            # print(len(one_clinic_name), len(one_clinic_address), len(one_clinic_mail_code))
            # if p % 20 == 0:
            #     time.sleep(random.random() * 10)

            if len(one_clinic_address) != len(one_clinic_name):
                one_clinic_address = [''] * len(one_clinic_name)
            if len(one_clinic_mail_code) != len(one_clinic_name):
                one_clinic_mail_code = [''] * len(one_clinic_name)

            for i in range(len(one_clinic_name)):
                res.append([one_clinic_name[i], one_clinic_address[i], one_clinic_mail_code[i]])

        except:
            print('{} {}页failed'.format(p_url[1], p))

    return res


if __name__ == '__main__':
    pro_urls = get_province_urls()
    clinic_list = []

    for pu in pro_urls:
        try:
            res = get_clinics_from_province_url(pu)
        except:
            print('{} failed!!'.format(pu[1]))

        curr_data = pd.DataFrame(res, columns=['名称', '地址', '邮编'])
        curr_data['省份'] = pu[1]
        curr_data.to_excel('./data/{}.xlsx'.format(pu[1]))

        print('{} finished!'.format(pu[1]))
