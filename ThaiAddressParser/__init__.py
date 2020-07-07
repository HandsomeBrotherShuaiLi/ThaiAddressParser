#!/usr/bin/env python
# encoding=utf-8
'''
@author: Shuai Li
@license: (C) Copyright 2015-2020, Shuai Li.
@contact: li.shuai@wustl.edu
@IDE: pycharm
@file: parser.py
@time: April 20 21:01
@desc:
'''
import os
import requests
from bs4 import BeautifulSoup
import tqdm
import json
import difflib
import random

def drop_nan(addr_list):
    '''
    drop useless parts of address list
    :param addr_list:
    :return:
    '''
    temp = []
    for a in addr_list:
        if len(a.replace('.', '').replace(' ', '').replace('/', '').replace('{', '').replace('}', '')
                       .replace('-', '').replace('(', '').replace(')', '')):
            temp.append(a)
    return temp


def check_th_chars(s):
    '''

    :param s:
    :return: check whether it contains thailand character or not
    '''
    TH_CHAR_RANGE = range(0x0E00, 0x0E7F + 1)
    Th_chars = set(map(chr, TH_CHAR_RANGE))
    t = []
    for c in s:
        if c in Th_chars:
            t.append(c)
    return len(t) > 0


def compute_similarity(str1, str2, mode=1):
    '''
    test the speed of similarity computation
    :param str1:
    :param str2:
    :param mode: mode 1 slower, mode 2 faster maybe
    :return:
    '''
    if mode == 1:
        similarity = difflib.SequenceMatcher(None, str1, str2).quick_ratio()
    else:
        similarity = len(set(str1) & set(str2))
    return similarity


def download_thai_address():
    print('Downloading the address information of Thailand ...')
    url = 'https://en.wikipedia.org/wiki/List_of_tambon_in_Thailand'
    data = requests.get(url).text
    data = BeautifulSoup(data, "html.parser")
    urls = data.find_all(name='ul')[0]
    hrefs = urls.find_all(name='li')
    res = {}
    th_en = {}
    for h in tqdm.tqdm(hrefs):
        href = 'https://en.wikipedia.org/' + h.find(name='a')['href']
        data = requests.get(href).text
        data = BeautifulSoup(data, 'html.parser')
        table = data.find_all(name='table', attrs={'class': 'wikitable sortable'})
        details = table[0].find_all(name='tr')[1:]
        for detail in details:
            temp = detail.find_all(name='td')
            sub_district = temp[1].text
            district = temp[3].text
            province = temp[5].text
            th_en[sub_district] = temp[0].text
            th_en[district] = temp[2].text
            th_en[province] = temp[4].text
            if province in res.keys():
                if district in res[province].keys():
                    if sub_district not in res[province][district]:
                        res[province][district].append(sub_district)
                else:
                    res[province][district] = [sub_district]
            else:
                res[province] = {district: [sub_district]}
    for p in res.keys():
        for d in res[p].keys():
            res[p][d] = list(set(res[p][d]))
    json.dump(res, open('th_provinces_districts_sub_districts.json', 'w', encoding='utf-8'),
              ensure_ascii=False)
    json.dump(res, open('th_en_db.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print('Finish the downloading!')


class ThaiAddressParserClass(object):
    def __init__(self,
                 file_path, translation_db):
        """

        :param file_path: {province:{district:[sub district，，，，，]}}
        """
        self.dictionary = json.load(open(file_path, 'r', encoding='utf-8'))
        self.th_en_translator = json.load(open(translation_db, 'r', encoding='utf-8'))
        self.sub_district_dict = {}
        self.district_dict = {}  # sub_district :[district, province]

        self.address_list = []
        self.thai_parts = []
        self.thai_parts_index = []
        self.bangkok_flags = []
        self.non_bangkok_province_index = []
        self.non_bangkok_sub_district_index = []
        self.non_bangkok_district_index = []
        self.o_province = []
        self.o_district = []
        self.o_sub_district = []

        self.bangkok_districts = []
        self.bangkok_sub_districts = []
        self.non_bangkok_provinces = []
        self.non_bangkok_districts = []
        self.non_bangkok_sub_districts = []

        for p in self.dictionary.keys():
            temp = self.dictionary[p]
            if p != 'กรุงเทพมหานคร':
                self.non_bangkok_provinces.append(p)
            for d in temp.keys():
                self.district_dict[d] = p
                if p == 'กรุงเทพมหานคร':
                    self.bangkok_districts.append(d)
                else:
                    self.non_bangkok_districts.append(d)
                sub_districts = temp[d]
                for s in sub_districts:
                    self.sub_district_dict[s] = [d, p]
                    if p == 'กรุงเทพมหานคร':
                        self.bangkok_sub_districts.append(s)
                    else:
                        self.non_bangkok_sub_districts.append(s)

    def parse(self, address):
        '''

        :param address: string type
        :return:
        '''
        self.address_list = address.split(' ')
        temp = []
        for idx, i in enumerate(self.address_list):
            if idx:
                i = i.strip(' ')
                if 'กรุงเทพมหานคร' in i:
                    t = i.index('กรุงเทพมหานคร')
                    if len(i[:t]):
                        temp[-1] += i[:t]
                    temp.append('กรุงเทพมหานคร')
                elif 'จ.' in i:
                    t = i.index('จ.')
                    if len(i[:t]):
                        temp[-1] += i[:t]
                    if len(i[(t + 2):]):
                        temp.append(i[t:])
                elif 'อ.' in i:
                    t = i.index('อ.')
                    if len(i[:t]):
                        temp[-1] += i[:t]
                    if len(i[(t + 2):]):
                        temp.append(i[t:])
                elif 'ต.' in i:
                    t = i.index('ต.')
                    if len(i[:t]):
                        temp[-1] += ' ' + i[:t]
                    if len(i[(t + 2):]):
                        temp.append(i[t:])
                else:
                    if len(i):
                        temp.append(i)
            else:
                if len(i):
                    temp.append(i)
        self.address_list = temp
        for idx, i in enumerate(self.address_list):
            i = i.strip(' ')
            if check_th_chars(i):
                self.thai_parts.append(i)
                self.thai_parts_index.append([i, idx])
                if i == 'กรุงเทพมหานคร':
                    self.bangkok_flags.append(len(self.thai_parts) - 1)
                if 'จ.' in i:
                    self.non_bangkok_province_index.append(len(self.thai_parts) - 1)
                    t = i.index('จ.')
                    self.o_province.append(i[(t + 2):])
                if 'อ.' in i:
                    self.non_bangkok_district_index.append(len(self.thai_parts) - 1)
                    t = i.index('อ.')
                    self.o_district.append(i[(t + 2):])
                if 'ต.' in i:
                    self.non_bangkok_sub_district_index.append(len(self.thai_parts) - 1)
                    t = i.index('ต.')
                    self.o_sub_district.append(i[(t + 2):])
        non_bangkok_index = self.non_bangkok_sub_district_index + self.non_bangkok_district_index + \
                            self.non_bangkok_province_index
        if len(self.bangkok_flags) and len(non_bangkok_index) == 0:
            try:
                res = self.parse_bangkok()
            except:
                detailed_address = ' '.join(self.address_list)
                province = 'กรุงเทพมหานคร'
                district = random.choice(list(self.dictionary['กรุงเทพมหานคร'].keys()))
                sub_district = random.choice(list(self.dictionary['กรุงเทพมหานคร'][district]))
                res = ['{} {} {} {}'.format(detailed_address, sub_district, district, province),
                       detailed_address, sub_district, district, province]
        elif len(self.bangkok_flags) == 0 and len(non_bangkok_index):
            try:
                res = self.parse_other_province()
            except:
                detailed_address = ' '.join(self.address_list)
                province = random.choice(self.non_bangkok_provinces)
                district = random.choice(list(self.dictionary[province].keys()))
                sub_district = random.choice(self.dictionary[province][district])
                res = ['{} {} {} {}'.format(detailed_address, sub_district, district, province),
                       detailed_address, sub_district, district, province]
        elif len(self.bangkok_flags) and len(non_bangkok_index):
            flags = [
                len(self.non_bangkok_district_index) >= 1,
                len(self.non_bangkok_sub_district_index) >= 1,
                len(self.non_bangkok_province_index) >= 1
            ]
            if sum(flags) >= 2:
                try:
                    res = self.parse_other_province()
                except:
                    detailed_address = ' '.join(self.address_list)
                    province = random.choice(self.non_bangkok_provinces)
                    district = random.choice(list(self.dictionary[province].keys()))
                    sub_district = random.choice(self.dictionary[province][district])
                    res = ['{} {} {} {}'.format(detailed_address, sub_district, district, province),
                           detailed_address, sub_district, district, province]
            else:
                try:
                    res = self.parse_bangkok()
                except:
                    detailed_address = ' '.join(self.address_list)
                    province = 'กรุงเทพมหานคร'
                    district = random.choice(list(self.dictionary['กรุงเทพมหานคร'].keys()))
                    sub_district = random.choice(list(self.dictionary['กรุงเทพมหานคร'][district]))
                    res = ['{} {} {} {}'.format(detailed_address, sub_district, district, province),
                           detailed_address, sub_district, district, province]
        else:
            try:
                res = self.parse_none_flags_address()
            except:
                detailed_address = ' '.join(self.address_list)
                province = random.choice(list(self.dictionary.keys()))
                district = random.choice(list(self.dictionary[province].keys()))
                sub_district = random.choice(self.dictionary[province][district])
                res = ['{} {} {} {}'.format(detailed_address, sub_district, district, province),
                       detailed_address, sub_district, district, province]

        self.address_list = []
        self.thai_parts = []
        self.thai_parts_index = []
        self.bangkok_flags = []
        self.non_bangkok_province_index = []
        self.non_bangkok_sub_district_index = []
        self.non_bangkok_district_index = []
        self.o_province = []
        self.o_district = []
        self.o_sub_district = []

        return res

    def parse_bangkok_sub_district(self, district, bangkok_idx):
        '''

        :param district:
        :param bangkok_idx:
        :return:
        '''

        if bangkok_idx - 2 >= 0:
            sub_district_candidate = self.thai_parts[bangkok_idx - 2]
            if sub_district_candidate in self.dictionary['กรุงเทพมหานคร'][district]:
                sub_district = sub_district_candidate
                original_index = self.thai_parts_index[bangkok_idx - 2][1]
                detailed_address = ' '.join(self.address_list[:original_index])
                prob = 1
            else:
                if bangkok_idx - 3 >= 0:
                    sub_district_candidate_2 = self.thai_parts[bangkok_idx - 3]
                    if sub_district_candidate_2 in self.dictionary['กรุงเทพมหานคร'][district]:
                        sub_district = sub_district_candidate_2
                        original_index = self.thai_parts_index[bangkok_idx - 3][1]
                        detailed_address = ' '.join(self.address_list[:original_index])
                        prob = 1
                    else:
                        '''
                        TODO:test the speed of difflib!
                        single ratio:0.008 ms
                        '''
                        max_degree_1 = 0
                        sub_1 = sub_district_candidate
                        max_degree_2 = 0
                        sub_2 = sub_district_candidate_2
                        for value in self.dictionary['กรุงเทพมหานคร'][district]:
                            degree_1 = compute_similarity(
                                value, sub_district_candidate, mode=1
                            )
                            degree_2 = compute_similarity(
                                value, sub_district_candidate, mode=1
                            )
                            # degree_1 = difflib.SequenceMatcher(None, value,
                            #                                    sub_district_candidate).quick_ratio()
                            # degree_2 = difflib.SequenceMatcher(None, value,
                            #                                    sub_district_candidate_2).quick_ratio()
                            if degree_1 > max_degree_1:
                                max_degree_1 = degree_1
                                sub_1 = value
                            if degree_2 > max_degree_2:
                                max_degree_2 = degree_2
                                sub_2 = value

                        if max_degree_1 >= max_degree_2:
                            sub_district = sub_1
                            original_index = self.thai_parts_index[bangkok_idx - 2][1]
                            detailed_address = ' '.join(self.address_list[:original_index])
                            prob = max_degree_1
                        else:
                            sub_district = sub_2
                            original_index = self.thai_parts_index[bangkok_idx - 3][1]
                            detailed_address = ' '.join(self.address_list[:original_index])
                            prob = max_degree_2
                else:
                    max_degree_1 = 0
                    sub_1 = sub_district_candidate
                    for value in self.dictionary['กรุงเทพมหานคร'][district]:
                        degree_1 = compute_similarity(value, sub_district_candidate, mode=1)
                        # degree_1 = difflib.SequenceMatcher(None, value,
                        #                                    sub_district_candidate).quick_ratio()
                        if degree_1 > max_degree_1:
                            max_degree_1 = degree_1
                            sub_1 = value
                    sub_district = sub_1
                    original_index = self.thai_parts_index[bangkok_idx - 2][1]
                    detailed_address = ' '.join(self.address_list[:original_index])
                    prob = max_degree_1
        else:
            original_index = self.thai_parts_index[bangkok_idx - 1][1]
            sub_district = random.choice(self.dictionary['กรุงเทพมหานคร'][district])
            detailed_address = ' '.join(self.address_list[:original_index])
            prob = 0
        return sub_district, detailed_address, prob

    def parse_bangkok_district_sub_district_detailed_address(self, bangkok_idx):
        if bangkok_idx - 1 >= 0:
            district_candidate = self.thai_parts[bangkok_idx - 1]
            if district_candidate in self.bangkok_districts:
                district = district_candidate
                sub_district, detailed_address, sub_district_prob = self.parse_bangkok_sub_district(district,
                                                                                                    bangkok_idx)
                prob = sub_district_prob
            else:
                if bangkok_idx - 2 >= 0:
                    district_candidate_2 = self.thai_parts[bangkok_idx - 2]
                    if district_candidate_2 in self.bangkok_districts:
                        district = district_candidate_2
                        sub_district, detailed_address, sub_district_prob = self.parse_bangkok_sub_district(district,
                                                                                                            bangkok_idx - 1)
                        prob = sub_district_prob
                    else:
                        max_degree_1 = 0
                        district_1 = district_candidate
                        max_degree_2 = 0
                        district_2 = district_candidate_2
                        for value in self.bangkok_districts:
                            degree_1 = compute_similarity(value, district_candidate, mode=1)
                            degree_2 = compute_similarity(value, district_candidate, mode=1)
                            # degree_1 = difflib.SequenceMatcher(None, value,
                            #                                    district_candidate).quick_ratio()
                            # degree_2 = difflib.SequenceMatcher(None, value,
                            #                                    district_candidate_2).quick_ratio()
                            if degree_1 > max_degree_1:
                                max_degree_1 = degree_1
                                district_1 = value
                            if degree_2 > max_degree_2:
                                max_degree_2 = degree_2
                                district_2 = value
                        if max_degree_1 >= max_degree_2:
                            district = district_1
                            sub_district, detailed_address, sub_district_prob = self.parse_bangkok_sub_district(
                                district,
                                bangkok_idx)
                            prob = max_degree_1 * sub_district_prob
                        else:
                            district = district_2
                            sub_district, detailed_address, sub_district_prob = self.parse_bangkok_sub_district(
                                district,
                                bangkok_idx - 1)
                            prob = max_degree_2 * sub_district_prob
                else:
                    max_degree_1 = 0
                    district_1 = district_candidate
                    for value in self.bangkok_districts:
                        degree_1 = compute_similarity(value, district_candidate, mode=1)
                        # degree_1 = difflib.SequenceMatcher(None, value,
                        #                                    district_candidate).quick_ratio()
                        if degree_1 > max_degree_1:
                            max_degree_1 = degree_1
                            district_1 = value
                    district = district_1
                    sub_district, detailed_address, sub_district_prob = self.parse_bangkok_sub_district(district,
                                                                                                        bangkok_idx)
                    prob = max_degree_1 * sub_district_prob
        else:
            district = random.choice(self.bangkok_districts)
            sub_district = random.choice(self.dictionary['กรุงเทพมหานคร'][district])
            original_index = self.thai_parts_index[bangkok_idx][1]
            detailed_address = ' '.join(self.address_list[:original_index])
            prob = 0
        return district, sub_district, detailed_address, prob

    def parse_bangkok(self):
        province = 'กรุงเทพมหานคร'
        district = 'null'
        sub_district = 'null'
        detailed_address = 'null'
        if len(self.bangkok_flags) == 1:
            bangkok_idx = self.bangkok_flags[0]
            district, sub_district, detailed_address, prob = self.parse_bangkok_district_sub_district_detailed_address(
                bangkok_idx)

        else:
            max_prob = 0
            for idx in self.bangkok_flags:
                t_district, t_sub_district, t_detailed_address, \
                prob = self.parse_bangkok_district_sub_district_detailed_address(
                    idx)
                if prob >= max_prob:
                    district = t_district
                    sub_district = t_sub_district
                    detailed_address = t_detailed_address

        result = ['{} {} {} {}'.format(detailed_address, sub_district, district, province),
                  detailed_address, sub_district, district, province]
        return result

    def parse_other_province(self):
        province = 'null'
        district = 'null'
        sub_district = 'null'
        detailed_address = 'null'
        if len(self.o_province) and len(self.o_district):
            inter_provinces = list(set(self.o_province) & set(self.non_bangkok_provinces))
            if len(inter_provinces):
                district_candidates = []
                for p in inter_provinces:
                    district_candidates += list(self.dictionary[p].keys())
                inter_districts = list(set(district_candidates) & set(self.o_district))
                if len(inter_districts):
                    sub_district_temp = []
                    for d in inter_districts:
                        p = self.district_dict[d]
                        sub_district_temp += self.dictionary[p][d]
                    inter_sub_districts = list(set(self.o_sub_district) & set(sub_district_temp))
                    if len(inter_sub_districts):
                        sub_district = inter_sub_districts[0]
                        district, province = self.sub_district_dict[sub_district]
                        idx = self.o_sub_district.index(sub_district)
                        idx = self.non_bangkok_sub_district_index[idx]
                        original_idx = self.thai_parts_index[idx][1]
                        detailed_address = ' '.join(self.address_list[:original_idx])
                    else:
                        if len(self.o_sub_district):
                            lens = [len(i) for i in self.o_sub_district]
                            max_index = lens.index(max(lens))
                            sub_district_candidate = self.o_sub_district[max_index]
                            max_degree = -1
                            for j in sub_district_temp:
                                degree = compute_similarity(j,
                                                            sub_district_candidate, mode=1)
                                if degree > max_degree:
                                    max_degree = degree
                                    sub_district = j
                            idx = self.non_bangkok_sub_district_index[max_index]
                            district, province = self.sub_district_dict[sub_district]
                            original_idx = self.thai_parts_index[idx][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
                        else:
                            district = inter_districts[0]
                            province = self.district_dict[district]
                            sub_district_candidates = self.dictionary[province][district]
                            d_idx = self.o_district.index(district)
                            d_idx = self.non_bangkok_district_index[d_idx]
                            if d_idx - 1 >= 0:
                                selected_sub_district = self.thai_parts[d_idx - 1]
                                max_degree = -1
                                for s in sub_district_candidates:
                                    degree = compute_similarity(selected_sub_district, s, mode=1)
                                    if degree > max_degree:
                                        max_degree = degree
                                        sub_district = s
                                original_idx = self.thai_parts_index[d_idx - 1][1]
                                detailed_address = ' '.join(self.address_list[:original_idx])
                            else:
                                sub_district = random.choice(sub_district_candidates)
                                original_idx = self.thai_parts_index[d_idx][1]
                                detailed_address = ' '.join(self.address_list[:original_idx])
                else:
                    max_degree = -1
                    re_idx = 0
                    for d_idx, d in enumerate(self.o_district):
                        for j in district_candidates:
                            degree = compute_similarity(j, d, mode=1)
                            if degree > max_degree:
                                max_degree = degree
                                district = j
                                re_idx = d_idx
                    province = self.district_dict[district]
                    sub_district_candidates = self.dictionary[province][district]
                    if len(self.o_sub_district):
                        lens = [len(i) for i in self.o_sub_district]
                        max_index = lens.index(max(lens))
                        sub_district_candidate = self.o_sub_district[max_index]
                        max_degree = -1
                        for j in sub_district_candidates:
                            degree = compute_similarity(j, sub_district_candidate, mode=1)
                            if degree > max_degree:
                                max_degree = degree
                                sub_district = j
                        idx = self.non_bangkok_sub_district_index[max_index]
                        original_idx = self.thai_parts_index[idx][1]
                        detailed_address = ' '.join(self.address_list[:original_idx])
                    else:
                        d_idx = self.non_bangkok_district_index[re_idx]
                        if d_idx - 1 >= 0:
                            sub_district_candidate = self.thai_parts[d_idx - 1]
                            max_degree = -1
                            for j in sub_district_candidates:
                                degree = compute_similarity(j, sub_district_candidate, mode=1)
                                if degree > max_degree:
                                    max_degree = degree
                                    sub_district = j
                            original_idx = self.thai_parts_index[d_idx - 1][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
                        else:
                            sub_district = random.choice(sub_district_candidates)
                            original_idx = self.thai_parts_index[d_idx][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
            else:
                inter_districts = list(set(self.o_district) & set(self.non_bangkok_districts))
                if len(inter_districts):
                    district = inter_districts[0]
                    province = self.district_dict[district]
                    sub_district_candidates = self.dictionary[province][district]
                    if len(self.o_sub_district):
                        lens = [len(i) for i in self.o_sub_district]
                        max_index = lens.index(max(lens))
                        sub_district_candidate = self.o_sub_district[max_index]
                        max_degree = -1
                        for j in sub_district_candidates:
                            degree = compute_similarity(j, sub_district_candidate, mode=1)
                            if degree > max_degree:
                                max_degree = degree
                                sub_district = j
                        idx = self.non_bangkok_sub_district_index[max_index]
                        original_idx = self.thai_parts_index[idx][1]
                        detailed_address = ' '.join(self.address_list[:original_idx])
                    else:
                        d_idx = self.o_district.index(district)
                        d_idx = self.non_bangkok_district_index[d_idx]
                        if d_idx - 1 >= 0:
                            selected_sub_district = self.thai_parts[d_idx - 1]
                            max_degree = -1
                            for s in sub_district_candidates:
                                degree = compute_similarity(selected_sub_district, s, mode=1)
                                if degree > max_degree:
                                    max_degree = degree
                                    sub_district = s
                            original_idx = self.thai_parts_index[d_idx - 1][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
                        else:
                            sub_district = random.choice(sub_district_candidates)
                            original_idx = self.thai_parts_index[d_idx][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
                else:
                    max_degree = -1
                    for p in self.o_province:
                        for j in self.non_bangkok_provinces:
                            degree = compute_similarity(p, j, mode=1)
                            if degree > max_degree:
                                max_degree = degree
                                province = j
                    district_candidates = list(self.dictionary[province].keys())
                    max_degree = -1
                    re_idx = 0
                    for d_idx, d in enumerate(self.o_district):
                        for j in district_candidates:
                            degree = compute_similarity(j, d, mode=1)
                            if degree > max_degree:
                                max_degree = degree
                                district = j
                                re_idx = d_idx
                    sub_district_candidates = self.dictionary[province][district]
                    if len(self.o_sub_district):
                        lens = [len(i) for i in self.o_sub_district]
                        max_index = lens.index(max(lens))
                        sub_district_candidate = self.o_sub_district[max_index]
                        max_degree = -1
                        for j in sub_district_candidates:
                            degree = compute_similarity(j, sub_district_candidate, mode=1)
                            if degree > max_degree:
                                max_degree = degree
                                sub_district = j
                        idx = self.non_bangkok_sub_district_index[max_index]
                        original_idx = self.thai_parts_index[idx][1]
                        detailed_address = ' '.join(self.address_list[:original_idx])
                    else:
                        if re_idx - 1 >= 0:
                            selected_sub_district = self.thai_parts[re_idx - 1]
                            max_degree = -1
                            for s in sub_district_candidates:
                                degree = compute_similarity(selected_sub_district, s, mode=1)
                                if degree > max_degree:
                                    max_degree = degree
                                    sub_district = s
                            original_idx = self.thai_parts_index[re_idx - 1][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
                        else:
                            sub_district = random.choice(sub_district_candidates)
                            original_idx = self.thai_parts_index[re_idx][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])

        elif len(self.o_province) and len(self.o_district) == 0:
            if len(self.o_sub_district):
                inter_provinces = list(set(self.o_province) & set(self.non_bangkok_provinces))
                if len(inter_provinces):
                    temp_districts = []
                    temp_sub_districts = []
                    for p in inter_provinces:
                        temp_districts += list(self.dictionary[p].keys())
                        for d in self.dictionary[p].keys():
                            temp_sub_districts += self.dictionary[p][d]
                    inter_sub_districts = list(set(self.o_sub_district) & set(temp_sub_districts))
                    if len(inter_sub_districts):
                        sub_district = inter_sub_districts[0]
                        district, province = self.sub_district_dict[sub_district]
                        idx = self.o_sub_district.index(sub_district)
                        idx = self.non_bangkok_sub_district_index[idx]
                        original_idx = self.thai_parts_index[idx][1]
                        detailed_address = ' '.join(self.address_list[:original_idx])
                    else:
                        max_degree = -1
                        re_idx = 0
                        for idx, i in enumerate(self.o_sub_district):
                            for j in temp_sub_districts:
                                degree = compute_similarity(i, j, mode=1)
                                if degree > max_degree:
                                    max_degree = degree
                                    sub_district = j
                                    re_idx = idx
                        district, province = self.sub_district_dict[sub_district]
                        idx = self.non_bangkok_sub_district_index[re_idx]
                        original_idx = self.thai_parts_index[idx][1]
                        detailed_address = ' '.join(self.address_list[:original_idx])
                else:
                    max_degree = -1
                    for p in self.o_province:
                        for t in self.non_bangkok_provinces:
                            degree = compute_similarity(p, t, mode=1)
                            if degree > max_degree:
                                max_degree = degree
                                province = t
                    temp_sub_districts = []
                    for d in self.dictionary[province].keys():
                        temp_sub_districts += self.dictionary[province][d]
                    inter_sub_districts = list(set(self.o_sub_district) & set(temp_sub_districts))
                    if len(inter_sub_districts):
                        sub_district = inter_sub_districts[0]
                        district, province = self.sub_district_dict[sub_district]
                        idx = self.o_sub_district.index(sub_district)
                        idx = self.non_bangkok_sub_district_index[idx]
                        original_idx = self.thai_parts_index[idx][1]
                        detailed_address = ' '.join(self.address_list[:original_idx])
                    else:
                        max_degree = -1
                        re_idx = 0
                        for idx, i in enumerate(self.o_sub_district):
                            for j in temp_sub_districts:
                                degree = compute_similarity(i, j, mode=1)
                                if degree > max_degree:
                                    max_degree = degree
                                    sub_district = j
                                    re_idx = idx
                        district, province = self.sub_district_dict[sub_district]
                        idx = self.non_bangkok_sub_district_index[re_idx]
                        original_idx = self.thai_parts_index[idx][1]
                        detailed_address = ' '.join(self.address_list[:original_idx])
            else:
                inter_provinces = list(set(self.o_province) & set(self.non_bangkok_provinces))
                if len(inter_provinces):
                    temp_districts = []
                    temp_sub_districts = []
                    province = inter_provinces[0]
                    temp_districts += list(self.dictionary[province].keys())
                    for d in self.dictionary[province].keys():
                        temp_sub_districts += self.dictionary[province][d]
                    p_idx = self.o_province.index(province)
                    p_idx = self.non_bangkok_province_index[p_idx]
                    if p_idx - 2 >= 0:
                        sub_district_candidate = self.thai_parts[p_idx - 2]
                        if sub_district_candidate in temp_sub_districts:
                            sub_district = sub_district_candidate
                            district, province = self.sub_district_dict[sub_district]
                            original_idx = self.thai_parts_index[p_idx - 2][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
                        else:
                            max_degree = -1
                            for x in temp_sub_districts:
                                degree = compute_similarity(sub_district_candidate, x)
                                if degree > max_degree:
                                    max_degree = degree
                                    sub_district = x
                            district, province = self.sub_district_dict[sub_district]
                            original_idx = self.thai_parts_index[p_idx - 2][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
                    else:
                        if p_idx - 1 >= 0:
                            district_candidate = self.thai_parts[p_idx - 1]
                            max_degree = -1
                            for d in temp_districts:
                                degree = compute_similarity(district_candidate, d, mode=1)
                                if degree > max_degree:
                                    max_degree = degree
                                    district = d
                            sub_district = random.choice(self.dictionary[province][district])
                            original_idx = self.thai_parts_index[p_idx - 1][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
                        else:
                            district = random.choice(temp_districts)
                            sub_district = random.choice(self.dictionary[province][district])
                            original_idx = self.thai_parts_index[p_idx][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
                else:
                    max_degree = -1
                    re_idx = 0
                    for p_idx, p in enumerate(self.o_province):
                        for t in self.non_bangkok_provinces:
                            degree = compute_similarity(p, t, mode=1)
                            if degree > max_degree:
                                max_degree = degree
                                province = t
                                re_idx = p_idx
                    temp_sub_districts = []
                    temp_districts = []
                    for d in self.dictionary[province].keys():
                        temp_districts.append(d)
                        temp_sub_districts += self.dictionary[province][d]
                    p_idx = self.non_bangkok_province_index[re_idx]
                    if p_idx - 2 >= 0:
                        sub_district_candidate = self.thai_parts[p_idx - 2]
                        if sub_district_candidate in temp_sub_districts:
                            sub_district = sub_district_candidate
                            district, province = self.sub_district_dict[sub_district]
                            original_idx = self.thai_parts_index[p_idx - 2][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
                        else:
                            max_degree = -1
                            for x in temp_sub_districts:
                                degree = compute_similarity(sub_district_candidate, x)
                                if degree > max_degree:
                                    max_degree = degree
                                    sub_district = x
                            district, province = self.sub_district_dict[sub_district]
                            original_idx = self.thai_parts_index[p_idx - 2][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
                    else:
                        if p_idx - 1 >= 0:
                            district_candidate = self.thai_parts[p_idx - 1]
                            max_degree = -1
                            for d in temp_districts:
                                degree = compute_similarity(district_candidate, d, mode=1)
                                if degree > max_degree:
                                    max_degree = degree
                                    district = d
                            sub_district = random.choice(self.dictionary[province][district])
                            original_idx = self.thai_parts_index[p_idx - 1][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
                        else:
                            district = random.choice(temp_districts)
                            sub_district = random.choice(self.dictionary[province][district])
                            original_idx = self.thai_parts_index[p_idx][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])

        elif len(self.o_province) == 0 and len(self.o_district):
            inter_districts = list(set(self.o_district) & set(self.non_bangkok_districts))
            if len(inter_districts):
                temp_sub_districts = []
                for j in inter_districts:
                    j_p = self.district_dict[j]
                    j_sub_districts = self.dictionary[j_p][j]
                    temp_sub_districts += j_sub_districts
                inter_sub_districts = list(set(self.o_sub_district) & set(temp_sub_districts))
                if len(inter_sub_districts):
                    sub_district = inter_sub_districts[0]
                    district, province = self.sub_district_dict[sub_district]
                    idx = self.o_sub_district.index(sub_district)
                    idx = self.non_bangkok_sub_district_index[idx]
                    original_idx = self.thai_parts_index[idx][1]
                    detailed_address = ' '.join(self.address_list[:original_idx])
                else:
                    if len(self.o_sub_district):
                        max_degree = -1
                        selected_o_sub_district = self.o_sub_district[0]
                        for i in self.o_sub_district:
                            for j in temp_sub_districts:
                                degree = compute_similarity(i, j, mode=1)
                                if degree > max_degree:
                                    max_degree = degree
                                    sub_district = j
                                    selected_o_sub_district = i
                        idx = self.o_sub_district.index(selected_o_sub_district)
                        idx = self.non_bangkok_sub_district_index[idx]
                        original_idx = self.thai_parts_index[idx][1]
                        district, province = self.sub_district_dict[sub_district]
                        detailed_address = ' '.join(self.address_list[:original_idx])
                    else:
                        district = inter_districts[0]
                        province = self.district_dict[district]
                        all_sub_districts = self.dictionary[province][district]
                        idx = self.o_district.index(district)
                        idx = self.non_bangkok_district_index[idx]
                        if idx - 1 >= 0:
                            max_degree = -1
                            sub_district = self.thai_parts[idx - 1]
                            for sub_district_candidate in all_sub_districts:
                                degree = compute_similarity(sub_district_candidate,
                                                            self.thai_parts[idx - 1], mode=1)
                                if degree > max_degree:
                                    max_degree = degree
                                    sub_district = sub_district_candidate
                            original_idx = self.thai_parts_index[idx - 1][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
                        else:
                            sub_district = random.choice(all_sub_districts)
                            original_idx = self.thai_parts_index[idx][1]
                            detailed_address = ' '.join(self.address_list[:original_idx])
            else:
                if len(self.o_sub_district):
                    inter_sub_districts = list(set(self.o_sub_district) & set(self.non_bangkok_sub_districts))
                    max_degree = -1
                    if len(inter_sub_districts):
                        for i in inter_sub_districts:
                            d, p = self.sub_district_dict[i]
                            for j in self.o_district:
                                degree = compute_similarity(j, d, mode=1)
                                if degree > max_degree:
                                    max_degree = degree
                                    district = d
                                    sub_district = i
                                    province = p
                        idx = self.o_sub_district.index(sub_district)
                        idx = self.non_bangkok_sub_district_index[idx]
                        original_idx = self.thai_parts_index[idx][1]
                        detailed_address = ' '.join(self.address_list[:original_idx])
                    else:
                        district_candidates = self.o_district
                        lens = [len(i) for i in district_candidates]
                        max_index = lens.index(max(lens))
                        district_candidate = district_candidates[max_index]
                        max_degree = -1
                        for j in self.non_bangkok_districts:
                            degree = compute_similarity(district_candidate,
                                                        j, mode=1)
                            if degree > max_degree:
                                max_degree = degree
                                district = j
                        province = self.district_dict[district]
                        sub_district_candidates = self.dictionary[province][district]
                        sub_districts_lens = [len(i) for i in self.o_sub_district]
                        max_index = sub_districts_lens.index(max(sub_districts_lens))
                        selected_sub_district = self.o_sub_district[max_index]
                        max_degree = -1
                        for s in sub_district_candidates:
                            degree = compute_similarity(s, selected_sub_district, mode=1)
                            if degree > max_degree:
                                sub_district = s
                        idx = self.non_bangkok_sub_district_index[max_index]
                        original_index = self.thai_parts_index[idx][1]
                        detailed_address = ' '.join(self.address_list[:original_index])
                else:
                    district_candidates = self.o_district
                    lens = [len(i) for i in district_candidates]
                    max_index = lens.index(max(lens))
                    district_candidate = district_candidates[max_index]
                    max_degree = -1
                    for j in self.non_bangkok_districts:
                        degree = compute_similarity(district_candidate,
                                                    j, mode=1)
                        if degree > max_degree:
                            max_degree = degree
                            district = j
                    province = self.district_dict[district]
                    sub_district_candidates = self.dictionary[province][district]
                    idx = self.non_bangkok_district_index[max_index]
                    if idx - 1 >= 0:
                        sub_district_temp = self.thai_parts[idx - 1]
                        max_degree = -1
                        for s in sub_district_candidates:
                            degree = compute_similarity(s,
                                                        sub_district_temp, mode=1)
                            if degree > max_degree:
                                max_degree = degree
                                sub_district = s
                        detailed_address = ' '.join(self.address_list[:(self.thai_parts_index[idx - 1][1])])
                    else:
                        sub_district = random.choice(sub_district_candidates)
                        detailed_address = ' '.join(self.address_list[:(self.thai_parts_index[idx][1])])

        else:
            sub_district_candidates = self.o_sub_district
            inter_sub_districts = list(set(sub_district_candidates) & set(self.non_bangkok_sub_districts))
            if len(inter_sub_districts):
                sub_district = inter_sub_districts[0]
                district, province = self.sub_district_dict[sub_district]
                idx = self.o_sub_district.index(sub_district)
                idx = self.non_bangkok_sub_district_index[idx]
                original_idx = self.thai_parts_index[idx][1]
                detailed_address = ' '.join(self.address_list[:original_idx])
            else:
                lens = [len(i) for i in sub_district_candidates]
                max_index = lens.index(max(lens))
                sub_district_candidate = sub_district_candidates[max_index]
                max_degree = -1
                for j in self.non_bangkok_sub_districts:
                    t = compute_similarity(sub_district_candidate, j,
                                           mode=1)
                    if t > max_degree:
                        max_degree = t
                        sub_district = j
                district, province = self.sub_district_dict[sub_district]
                idx = self.non_bangkok_sub_district_index[max_index]
                original_idx = self.thai_parts_index[idx][1]
                detailed_address = ' '.join(self.address_list[:original_idx])

        result = ['{} {} {} {}'.format(detailed_address, 'ต.' + sub_district, 'อ.' + district, 'จ.' + province),
                  detailed_address, sub_district, district, province]
        return result

    def parse_none_flags_address(self):
        province = 'null'
        district = 'null'
        sub_district = 'null'
        detailed_address = 'null'
        if len(self.thai_parts) >= 3:
            province_candidate = self.thai_parts[-1]
            if province_candidate in self.dictionary.keys():
                province = province_candidate
            else:
                max_degree = -1
                for i in list(self.dictionary.keys()):
                    degree = compute_similarity(province_candidate, i, mode=1)
                    if degree > max_degree:
                        max_degree = degree
                        province = i
            district_candidates = list(self.dictionary[province].keys())
            district_candidate = self.thai_parts[-2]
            max_degree = -1
            for i in district_candidates:
                degree = compute_similarity(i, district_candidate, mode=1)
                if degree > max_degree:
                    max_degree = degree
                    district = i
            sub_district_candidates = self.dictionary[province][district]
            sub_district_candidate = self.thai_parts[-3]
            max_degree = -1
            for i in sub_district_candidates:
                degree = compute_similarity(i, sub_district_candidate, mode=1)
                if degree > max_degree:
                    max_degree = degree
                    sub_district = i
            idx = self.thai_parts_index[-3][1]
            detailed_address = ' '.join(self.address_list[:idx])
        elif len(self.thai_parts):
            total = ' '.join(self.thai_parts)
            max_degree = -1
            for i in list(self.dictionary.keys()):
                degree = compute_similarity(total, i, mode=1)
                if degree > max_degree:
                    max_degree = degree
                    province = i
            district_candidates = list(self.dictionary[province].keys())
            max_degree = -1
            for i in district_candidates:
                degree = compute_similarity(i, total, mode=1)
                if degree > max_degree:
                    max_degree = degree
                    district = i
            sub_district_candidates = self.dictionary[province][district]
            max_degree = -1
            for i in sub_district_candidates:
                degree = compute_similarity(i, total, mode=1)
                if degree > max_degree:
                    max_degree = degree
                    sub_district = i
            idx = self.thai_parts_index[0][1]
            detailed_address = ' '.join(self.address_list[:idx])
        else:
            result = ['null', 'null', 'null', 'null', 'null']
            return result
        if province != 'กรุงเทพมหานคร':
            result = ['{} {} {} {}'.format(detailed_address, 'ต.' + sub_district, 'อ.' + district, 'จ.' + province),
                      detailed_address, sub_district, district, province]
        else:
            result = ['{} {} {} {}'.format(detailed_address, sub_district, district, province),
                      detailed_address, sub_district, district, province]
        return result


def parse(address):
    if os.path.exists('th_provinces_districts_sub_districts.json') and os.path.exists('th_en_db.json'):
        app = ThaiAddressParserClass(file_path='th_provinces_districts_sub_districts.json',
                                     translation_db='th_en_db.json')
    else:
        download_thai_address()
        app = ThaiAddressParserClass(file_path='th_provinces_districts_sub_districts.json',
                                     translation_db='th_en_db.json')
    res = app.parse(address)
    return {
        'original_address': address,
        'parsed_address': res[0],
        'province': {'Thai': res[-1], 'En': app.th_en_translator[res[-1]]},
        'district': {'Thai': res[-2], 'En': app.th_en_translator[res[-2]]},
        'sub_district': {'Thai': res[-3], 'En': app.th_en_translator[res[-3]]},
        'remaining_address': res[-4]
    }
