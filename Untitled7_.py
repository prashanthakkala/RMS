#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import fnmatch, os, pythoncom, sys, win32com.client
import time
from difflib import SequenceMatcher as SM
import copy                        
import pdfplumber                  
import os
import spacy
from spacy.matcher import Matcher
from spacy.matcher import Matcher
import spacy
import pandas as pd
import random               
import warnings             
import re
import pdfplumber
from spacy.matcher import PhraseMatcher
from spacy.lang.en.stop_words import STOP_WORDS
import shutil
from unidecode import unidecode
import subprocess
from datetime import datetime
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import win32com.client
import pythoncom
from rms_features import Experience,Email,Mobile_number
# from wordtopdf import word_2_pdf
wdFormatPDF = 17 

conn_string = "mongodb://localhost:27017/"
client = MongoClient(conn_string)
db = client['RMS']


def mongo_insert(resume_lst,col_name):
    from pymongo import MongoClient
    conn_string = "mongodb://localhost:27017"
    client = MongoClient(conn_string)
    db = client['RMS']

    # print("------------------------------inserting data into MongoDb--------------------------------")
    Resume_col = db[col_name]
    Resume_col.insert_many(resume_lst)
    return "data Inserted"

Resume_skills = db['updated_skill_list'] # Skills_list
t_list = list(Resume_skills.find({},{'skill':1,'_id':0}))

skill_lst = []
for i in t_list:
    skill_lst.append(i['skill'].lower().strip())

skill_lst = list(set(skill_lst))
skill_lst.sort(key = len, reverse = True)



Resume_locations = db['Location_list']
l_list = list(Resume_locations.find({},{'location':1,'_id':0}))
list_city = []
for i in l_list:
    list_city.append(i['location'].lower())
list_city.sort(key = len, reverse = True)
list_city = list(set(list_city))


def multi_kv(wordslist_):
    wordslist = copy.deepcopy(wordslist_)
    words_temp = []
    for i in range(len(wordslist)):
        if len(words_temp) == 0:    
            wordslist[i]['text'] = str(wordslist[i]['text']).replace('`','').replace('.','').replace('Candidate','')
            words_temp.append(wordslist[i])
        else:
            wordslist[i]['text'] = str(wordslist[i]['text']).replace('.','').replace('Candidate','')
            diff_val = abs(words_temp[len(words_temp)-1]['x1'] - wordslist[i]['x0'])
            diff_ = abs(words_temp[len(words_temp) - 1]['top'] - wordslist[i]['top'])
            mail_check = 'email' not in wordslist[i]['text'].lower()
            comma_check = ',' not in words_temp[len(words_temp)-1]['text']
            dash_check = '-' not in words_temp[len(words_temp)-1]['text']
            if diff_val >=0 and diff_val <= 9 and diff_ < 4.5 and dash_check and mail_check and comma_check:
                words_temp[len(words_temp)-1]['text'] = words_temp[len(words_temp)-1]['text']+' ' +wordslist[i]['text']
                words_temp[len(words_temp)-1]['x0'] = sorted(list(set([words_temp[len(words_temp)-1]['x0'], wordslist[i]['x0']])))[0]
                words_temp[len(words_temp)-1]['x1'] = sorted(list(set([words_temp[len(words_temp)-1]['x1'], wordslist[i]['x1']])))[-1]

            else:
                words_temp.append(wordslist[i])
            if '-' in words_temp[len(words_temp)-2]['text']:
                words_temp[len(words_temp)-2]['text'] = words_temp[len(words_temp)-2]['text'].replace('-','').strip()
    return words_temp


# In[ ]:


def clean_data(text, name = None):
    punctuation = [',','-','+']  
    if type(text) == type(['test']):
        text = text[0]
    if text != None:
        for punc_ in punctuation:
            if punc_ in text.upper():
                text = text.replace(punc_, '')
        for skill in skill_lst:
            if len(skill) > 2:
                text = [i for i in text.split(' ') if SM(None,i.lower().strip(),skill).ratio() < 0.9]
                text = ' '.join(text)
        for city in list_city:
            if city in text.capitalize():
                text = text.capitalize().replace(city, '')        
        return text.replace('Email','').strip()
    else:
        pass


# In[ ]:


def concatenate_list(lst):
    result= ''
    for element in lst:
        if len(result) == 0:
            result += str(element)
        else:
            result += ' '+str(element)
    return result



# In[ ]:


def matcher_(wrds_lst_):
    wrds_lst = copy.deepcopy(wrds_lst_)
    tmp_mail = [i for i in wrds_lst if '@' in i]
    for wrd in wrds_lst:
        if 'Mobile' in wrd or 'PH:' in wrd:
            wrd_ = wrd.split('Mobile')[0].split('PH:')[0]
            wrds_lst[wrds_lst.index(wrd)] = wrd_.strip()
        if 'mr.' in wrd.lower() and len(wrd) < 4:
            wrd_index = wrds_lst.index(wrd)
            wrds_lst[wrd_index] = wrd + wrds_lst[wrd_index+1]
        if 'mail' in wrd.lower():
            mail_idx = wrds_lst_.index(wrd)
            mtch = wrds_lst[:mail_idx]
            mtch = [wrd.split(',')[0] for wrd in mtch]
            mtch = [vlu.replace(')','').strip() for vlu in mtch]
            if len(mtch) == 0:
                mail_sq = None
                if '@' in wrd.lower():
                    s_wrd = str(copy.deepcopy(wrd))
                    mail_sq = re.findall(re.compile(r'[^0-9@]+'), s_wrd)
                    mtch = wrds_lst[mail_idx+1: mail_idx + 4]
                else:
                    s_wrd = str(wrds_lst[mail_idx + 1])
                    if '@' in s_wrd:
                        mtch = wrds_lst[mail_idx+2: mail_idx + 5]
                        mail_sq = re.findall(re.compile(r'[^0-9@]+'), s_wrd)
                mtch_dum = copy.deepcopy(mtch)
                if mail_sq:
                    # print('mail_sq value condition is:', mail_sq)
                    mail_sq = ''.join(mail_sq[0].split()).lower().replace('-','').replace('email','').replace('mailid','').strip()
                    # print('cleaned mail_sq value is:', mail_sq)
                    # print('sm_value for mtch is:',[SM(None,mail_sq,i.lower()).ratio() for i in mtch if SM(None,mail_sq,i.lower()).ratio() > 0.4])
                    mtch = [i for i in mtch if SM(None,mail_sq,i.lower()).ratio() > 0.4]
                    # print('mtch value for sequence:', mtch)
                    if len(mtch) == 0:
                        # print('sequence split condition')
                        # print('mtch_dum value is:', mtch_dum)
                        mtch = []
                        for wrd_mtch in mtch_dum:
                            wrd_spl_ = wrd_mtch.split(' ')
                            # wrd_spl_ = [dupli_letter(i) for i in wrd_spl]
                            splt_mtch = SM(None, ''.join(wrd_spl_).lower(), mail_sq).ratio()
                            if splt_mtch > 0.4:
                                mtch.append(wrd_mtch)
                                break
                            else:
                                tmp_ = [i for i in wrd_spl_ if SM(None,mail_sq,i.lower()).ratio() > 0.4]
                                if len(tmp_) > 0:
                                    mtch.append(wrd_mtch)
                                    break
                                elif len(tmp_) == 0 and len(wrd_spl_) >= 3:
                                    wrd_spl_2 = ''.join(wrd_spl_[1:3])
                                    splt_mtch_2 = SM(None, wrd_spl_2.lower(), mail_sq).ratio()
                                    if splt_mtch_2 > 0.4:
                                        mtch.append(wrd_mtch)
                                        break
            if len(mtch) == 0:
                if '@' in wrd.lower():
                    mail_sq = re.findall(re.compile(r'[^0-9@]+'), wrd)
                    if mail_sq:
                        mail_sq = ''.join(mail_sq[0].split()).lower().replace('-','').replace('email','').replace('mailid','').strip()
                        mtch = [i for i in all_wrds if SM(None,mail_sq,i.lower()).ratio() > 0.4]
                elif '@' in wrds_lst[mail_idx + 1]:
                    mail_sq = re.findall(re.compile(r'[^0-9@]+'),wrds_lst[mail_idx + 1])
                    if mail_sq:
                        mail_sq = ''.join(mail_sq[0].split()).lower().replace('-','').replace('email','').replace('mailid','').strip()
                        mtch = [i for i in all_wrds if SM(None,mail_sq,i.lower()).ratio() > 0.4]
            fnl_mtch = []
            cnt = 0
            for vlu_ in mtch:
                vlu = ''.join(vlu_.split()).lower().replace('.','').replace(',','')
                if vlu.isalpha():
                    fnl_mtch.append(vlu_)
                else:
                    if len(fnl_mtch) == 1:
                        if len(fnl_mtch[0]) < 3:
                            fnl_mtch = []
                    elif len(fnl_mtch) == 0 and not vlu.isalpha():
                        continue
                    else:
                        break
            # print('fnl_mtch value is:', fnl_mtch)
            if len(fnl_mtch) > 0:
                if len(fnl_mtch[0].split(' ')) >= 2:
                    if len(fnl_mtch[0].split(' ')[0].split(' ')[0]) > 1:
                        return fnl_mtch[0]
                    else:
                        single_vlu = [i for i in fnl_mtch if len(i) == 1]
                        if len(single_vlu) > 2:
                            return concatenate_list(single_vlu)
                        else:
                            return concatenate_list(fnl_mtch[:2])
                elif len(fnl_mtch) < 4:         
                    return concatenate_list(fnl_mtch)
        else:
            if len(wrds_lst[0]) == 1 and wrds_lst[0] == wrds_lst[0].upper():
                return concatenate_list(wrds_lst[:2])
            elif len(wrds_lst[0]) == 1 and wrds_lst[0] != wrds_lst[0].upper() and len(wrds_lst[1]) > 1:
                return wrds_lst[1:2]
    return wrds_lst[0]


# In[ ]:


def stop_word_(words_, stop_wrds):
    words = copy.deepcopy(words_)
    word_s = []
    for stp_wrd in stop_wrds:
#         print('stp_wrd: ', stp_wrd)
        if len(word_s) == 0:
            word_s_ = [word['text'].split('(')[0].split('–')[0].strip() for word in words]
            word_s = [word for word in word_s_ if stp_wrd not in ''.join(word.upper().split())]
            word_s = [word for word in word_s if SM(None, word.upper(), stp_wrd).ratio() < 0.9]
#             print('if condition word_s: ', word_s)
        else:
            word_s = [word for word in word_s if stp_wrd not in ''.join(word.upper().split())]
            word_s = [word for word in word_s if SM(None, word.upper(), stp_wrd).ratio() < 0.9]
#             print('else word_s condition:', word_s)
#         cleaned_wrds.append(cln_wrds)
    cleaned_wrds = word_s
#     print('cleaned_wrds:', cleaned_wrds)
    
    if len(cleaned_wrds) > 0:
        if ('Mobile' in cleaned_wrds[0]) or ('PH:' in cleaned_wrds[0]):  #[-1].isnumeric():
            mb_cd = cleaned_wrds[0].replace('Mobile','').replace('PH:','')
            mb_cd1 = re.findall(re.compile(r'[a-zA-Z .]+'), mb_cd)
            if len(mb_cd1) > 0:
                mb_cd1 = mb_cd1[0].strip()
    #         mb_cd1 = mb_cd[0].strip()
    #         mb_cd2 = mb_cd[-1].strip()
                if len(mb_cd1) > 3 and ''.join(mb_cd1.split()).replace('.','').isalpha():
#                     print('mb_cd1 value is:', mb_cd1)
                    return clean_data(mb_cd1)    

        if ''.join(cleaned_wrds[0].split())[-4:-1].isnumeric():
            data_num = cleaned_wrds[1]
            if ''.join(data_num.split()).isalpha():
                if len(data_num) > 2:
                    return clean_data(data_num)
            if ''.join(cleaned_wrds[2].split()).isalpha():
                if len(cleaned_wrds[2]) > 2:
                    return clean_data(cleaned_wrds[2])
            else:
                return clean_data(cleaned_wrds[3])
        else:
    #         return cleaned_wrds[0]
            return matcher_(cleaned_wrds)
    else:
        return


# In[ ]:


def longestSubstring(str1,str2):
    seqMatch = SM(None,str1,str2)
    match = seqMatch.find_longest_match(0, len(str1), 0, len(str2))
    if (match.size!=0):
        return str1[match.a: match.a + match.size]
    else:
        return


# In[ ]:


def name_comparator(name_ext_, text):
    name_ext = copy.deepcopy(name_ext_)
    if name_ext != None:

        if cd == 'last':
            start = text.find(name_ext[:3], len(text) - 150)
            end = len(text)
        else:
            start = text.find(name_ext[:3])
            end = start + len(name_ext)

        text_value = text[start:end]

        
        sm_value = SM(None, name_ext, text_value).ratio()
#         print('sm_value is:', sm_value)
        if sm_value == 1:
            pass
        elif sm_value == 0:
            return text,'-', [-1, 0, 'UNLABELED']
        elif sm_value < 0.90:
            name_ext = longestSubstring(text_value, name_ext)
#             print('new name_ext:', name_ext)
            start = text.find(name_ext)
            end = start + len(name_ext)

        else:
            name_ext_vf = ''.join(name_ext.split(' '))
            vf_ = ''.join(text_value.split(' '))
            diff_name = abs(len(name_ext_vf) - len(vf_))
            start = text.find(name_ext[:3])
            end = start + len(name_ext) + diff_name

        return text, text[start:end], [start, end, 'NAME']
    else:
        return text, name_ext, [-1, 0, 'UNLABELED']


# In[ ]:


def name_extractor_plumber(path_, txt_file_name_, file_cnt):
    # print('path_ value is:', path_, '\n')
    path = path_+'\\'+txt_file_name_+'.pdf'
    txt_file_name = path_+'\\'+txt_file_name_+'.txt'

    global cd
    cd = 'name'
    # for idx in range(len(pdf_files)):
    try:
        with pdfplumber.open(path) as pdf:
            name_ext = None
            pdf_pages = len(pdf.pages)

        #     pdf = pdfplumber.open(path)
            if pdf_pages > 0:
                wrds_all = [pdf.pages[idx].dedupe_chars(tolerance=1).extract_words() for idx in range(len(pdf.pages))]
        #         print('wrds_all value is:\n', wrds_all)
                text = '\n'.join([pdf.pages[i].dedupe_chars(tolerance=1).extract_text() for i in range(len(pdf.pages))])
                text = clean_text_(text)
                
                wrds_length = len(wrds_all)
            else:

                return 'No pages', 'No pages', [-1, 0, 'UNLABELED']
    except Exception as err:
        print('Pdf error is:', err)
        return 'No pages', 'No pages', [-1, 0, 'UNLABELED']
    
    txt_length = len(text)

    if txt_length > 0:

        wrds = wrds_all[0]
        if len(wrds) <= 1 and wrds_length > 1:
            wrds = wrds_all[1]
#         else:
#             return 'No pages', 'No pages', [-1, 0, 'UNLABELED']
#         print('wrds value is:', wrds)
        global all_wrds
        prcss_wrds = multi_kv(wrds)
#         print('prcss_wrds:', prcss_wrds[:5])
        all_wrds = [i['text'] for i in prcss_wrds]
#         print('prcss_wrds:', prcss_wrds)
        mtch = list(filter(lambda x: 'name' in x['text'].lower(), prcss_wrds[:25]))
#         names = []
        if len(mtch) > 0:
            cd = 'name'
            matched_idx = prcss_wrds.index(mtch[0])

            matched = prcss_wrds[matched_idx:matched_idx+3]
    #         print('matched value is:', matched)
            if ':' in matched[0]['text']:
                match_sel = matched[0]['text'].split(':')
            elif '–' in matched[0]['text']:
                match_sel = matched[0]['text'].split('–')
            elif '-' in matched[0]['text']:
                match_sel = matched[0]['text'].split('-')
            else:
                match_sel = matched[0]['text']
            match_sel_idx = prcss_wrds.index(matched[0])
            mtch = [wrd for wrd in  match_sel if SM(None, 'name', wrd.lower()).ratio() > 0.85]
#             print('mtch value is:', mtch)
            if len(match_sel) == 2 and len(mtch) == 1:

                name_ext = match_sel[1].replace('-','').strip()
                if len(name_ext) < 3:
#                     name_ext = name_ext + ' ' + prcss_wrds[match_sel_idx+1]['text']
                    name_ext = name_ext + ' ' + matched[1]['text']
    #             print('single name_ext:\n', name_ext)
                    if len(name_ext) < 3:
                        name_ext = name_ext + ' ' + matched[2]['text']


            elif len(match_sel) == 1 and len(mtch) == 1 or match_sel[0] == 'Candidate Full Name (As Per Aadhar':
                name_ext = matched[1]['text']   #.split(':')[-1]
                if name_ext.lower() == 'card)':
                    name_ext = matched[2]['text']
                else:
                    name_ext = name_ext.split(':')[-1]
                    if len(name_ext) < 3:
                        name_ext = name_ext + ' ' + matched[2]['text']
            else:
                name_ext = None
        if name_ext == None:
            cd = 'first'

            name_stop_words = ['JOB','AADHAR','SUMMARY', 'INFO','INTRODUCTION','TECHNICAL','SKILL','CLOUD',
                               'CAREER', 'CONSULTANT', 'RESUM E', 'OBJECTIVES', 'ADDRESS', 'PRACTITIONER',
                               'ADMINISTRATOR','NACHARAM','NOIDA','PROFILE', 'HYDERABAD', 'CERTIFIED',
                               'INDIA', 'DELHI', 'CONTACT','ENGINER', 'TEST', 'CURRICULAM','ADMIN', 'ONENOTE',
                               'VITAE', 'RESUME', 'AWS', 'DEVOPS', 'ENGINEER', 'HADOOP',
                               'DEVELOPER', 'LOCATION', '', 'ANALYST', 'BANGALORE', 'KARNATAKA',
                              'SERVICE', '.NET', 'EDUCATION', 'DEVELOPMENT', 'PLACE', 'EXPERIENCE']
            
            name_ext = stop_word_(prcss_wrds[:25], name_stop_words)
#             print('name_ext value is:', name_ext)
            name_ext = clean_data(name_ext)
            if name_ext == None or '@' in name_ext:
                name_ext = None
    #         print('name_wrds:', name_ext)
            if name_ext == None or len(name_ext) < 3:
                cd = 'last'
                place_idx = text.lower().find('place', txt_length- 150)
                date_idx = text.lower().find('date', txt_length- 150)

                min_ = min(place_idx, date_idx)
                max_ = max(place_idx, date_idx)
                name_lst = text[min_:]

                doc_lst = nlp(name_lst)

                name_ppn = [tkn.text for tkn in doc_lst if tkn.pos_ == 'PROPN']
#                 print('proper nouns_lst:', name_ppn)
                if len(name_ppn) > 0:
                    name_lst = text[text.find(name_ppn[-1], min_):].replace('Place','').replace('Date','').replace(':','')
                text_, name_ext, annot = name_comparator(name_lst, text)
                if len(name_ext) < 3:
                    name_ext = '-'
                    annot = [-1, 0, 'UNLABELED']

                return text, name_ext, annot

            doc_fst = nlp(name_ext)
        name_ext = name_ext.replace('▪','').replace(',','').replace('+','').replace('=','').strip()

        data,name_final, annot = name_comparator(name_ext, text)
        # print('\n name value is:', name_final)
        if len(name_final) < 3:
            name_final = '-'
            annot = [-1, 0, 'UNLABELED']
        
        return data, name_final, annot
    
    else:
        # print('check else')
        return 'No pages', 'No pages', [-1, 0, 'UNLABELED']



# In[ ]:


def clean_text_(text):
    text = text.replace('\n',' ')
    text = text.replace('\uf0fc', '')
    text = text.replace('\uf0b7', '')
    text = text.replace('•',' ')
    text = text.replace('⮚',' ')
    text = text.replace('■',' ')
    text = text.replace('▪',' ')
    text = text.replace('●',' ')
    text = text.strip().split('   ')
    text = ' '.join([vlu for vlu in text if len(vlu) > 0])
    text = ' '.join(text.split('  '))
    return text.strip()




# In[ ]:


def location_extractor(txt_data, list_city, start_, skill_):
    skill_values = [i.lower() for i in skill_[0]]
    skill_annot = [i for i in skill_[1]]
    matched = []
    annotations = []
    annotations_idx_check = list(range(start_))
    location_txt = txt_data.lower()
    for city in list_city:
        # print('city value is:', city)
        city_skill_chk = [i for i in skill_values if city in i]
        if len(city_skill_chk) > 0:
            city_skill_chk = city_skill_chk[0]
            # print('city skill match:', city)
            idx_ = skill_values.index(city_skill_chk)
            annotations_idx_check.extend(list(range(1 , skill_annot[idx_][1])))
        if city in location_txt:
            location_strt = location_txt.find(city)
            location_strt_chk = location_strt
            location_end = location_strt + len(city)
            if (location_strt+1 not in annotations_idx_check) and (location_end-1 not in annotations_idx_check):
                text_checking = [i for i in txt_data[location_strt-1:location_end+1] if i.isalpha()]

                if txt_data[location_strt:location_end] == '' or len(city.replace(' ','').strip()) != len(text_checking):
                    # print('This location/dontknow not added: ', txt_data[location_strt:location_end])
                    continue
                else:
                    matched.append(city)
                    annotations.append([location_strt, location_end, 'LOCATION'])
                    [annotations_idx_check.append(i) for i in list(range(location_strt, location_end))]
            else:
                for loop_ in range(6):
                    location_strt = location_txt.find(city, location_strt_chk+1)
                    if (location_strt == -1) or (location_strt in annotations_idx_check):
                        location_end = 0
                        continue
                    else:
                        location_end = location_strt + len(city)
                        [annotations_idx_check.append(i) for i in list(range(location_strt, location_end))]
                        break
                text_checking = [i for i in txt_data[location_strt-1:location_end+1] if i.isalpha()]

                if txt_data[location_strt:location_end] == '' or len(city.replace(' ','').strip()) != len(text_checking):
                    # print('This location/dontknow not added: ', txt_data[location_strt:location_end])
                    pass
                else:
                    matched.append(txt_data[location_strt:location_end])
                    annotations.append([location_strt, location_end, 'LOCATION'])
        else:
            continue

    if len(matched) > 0:
        return ','.join(list(set(matched))), annotations
    else:
        return '-', [[-1,0, 'UNLABELED']]




def skill_extractor(txt_file, skill_lst, start_):
    skill_lst_ = [i.lower() for i in skill_lst if i != 'etl']
    skill_name = []
    skill_idx = []
    skill_idx_check = list(range(start_))
    skill_cnt = 0
    skill_txt = txt_file.lower()
    
    for skill in skill_lst_:
        # print('--'*85)
        # print('skill_idx_check value is:', skill_idx_check)
        if skill in skill_txt and len(skill) > 2:
            skill_strt = skill_txt.find(skill.lower())
            skill_strt_chk = skill_strt
            skill_end = skill_strt + len(skill)

            
            if (skill_strt not in skill_idx_check) and (skill_end-1 not in skill_idx_check):
                # print('no index matched')
                skill_name.append(skill)
                skill_idx.append([skill_strt, skill_end, 'SKILL'])
                [skill_idx_check.append(i) for i in list(range(skill_strt, skill_end))]
                # print('range appended:', skill_idx_check)
            else:
                # print('index matched')
                for loop_ in range(6):
                    skill_strt = skill_txt.find(skill.lower(), skill_strt_chk+3)
                    # print('new_loop start value:', skill_strt, 'loop-->', loop_+1)
                    if (skill_strt == -1) or (skill_strt in skill_idx_check) or (skill_end-1 in skill_idx_check):
                        skill_end = 0
                        continue
                    else:
                        skill_end = skill_strt + len(skill)

                        [skill_idx_check.append(i) for i in list(range(skill_strt, skill_end))]
                        break
                if txt_file[skill_strt:skill_end] == '':
                    pass
                else:
                    skill_name.append(txt_file[skill_strt:skill_end])
                    skill_idx.append([skill_strt, skill_end, 'SKILL'])
        else:
            continue

    if len(skill_name) > 0:
        return skill_name,skill_idx
    else:
        return ['-'], [[-1, 0, 'UNLABELED']]


# In[ ]:


def file_name_mod(f):  
    file_name = os.path.splitext(f)[0]
    if file_name.find("."):
        new_file_name = file_name.replace(".","")
    else:
        new_file_name = file_name
    return new_file_name



def single_file_pdfannotator(root, sub_folder,file):
    train_data = []
    text_data = []
    skill = []
    skill_idx = []
    location = []
    location_idx = []
    cv_idx = 0
    path_to_file = os.path.join(root,sub_folder, file)

    [stem, ext] = os.path.splitext(path_to_file)

    if ext.lower() == '.pdf':
    #                 print("Processing " + path_to_file)
        if '~$' not in path_to_file:
        #                     cv_list.append(path_to_file)
            path_to_txt = stem + ".txt"

#             print("path_to_txt",path_to_txt)

            #                     print('root value is:',root, '\n', 'stem value is:', stem)
            stem1 = stem.split("\\")[-1]
           
            

            file_path_chk = os.path.join(root, sub_folder)
            data_CV, name,name_id = name_extractor_plumber(file_path_chk, stem1, cv_idx+1)
            mobile_instance = Mobile_number(data_CV)
            mb_nmb, mb_ant = mobile_instance.extractor()

            email_instance = Email(data_CV)
            email_, em_ant = email_instance.extractor()

            if name_id[0] != -1 or em_ant[0] != -1:
                start = max(name_id[1], em_ant[1])
                skill_extraction_ = skill_extractor(data_CV, skill_lst, start)
                location_extractor_ = location_extractor(data_CV, list_city, start, skill_extraction_)
            else:
                start = 0
                skill_extraction_ = skill_extractor(data_CV, skill_lst, start)
                location_extractor_ = location_extractor(data_CV, list_city, start, skill_extraction_)
            skill.append(list(skill_extraction_[0]))
            # print('skill extraction values:', list(skill_extraction_[0]))
            skill_idx.append(skill_extraction_[1])
            # print('skill annotation values:', skill_extraction_[1])
            
            
            location.append(location_extractor_[0])
            location_idx.append(location_extractor_[1])
            #exp.append(exp_extractor(data_CV)[0])
            exp_instance = Experience(data_CV)
            exp = exp_instance.extractor()[0]
            exp_idx = exp_instance.extractor()[1]
            # exp = exp_extractor(data_CV)[0]
            # exp_idx = exp_extractor(data_CV)[1]
#             exp_idx.append(exp_extractor(data_CV)[1])
            train_data.append([data_CV, {'entities' : [name_id, mb_ant, em_ant, exp_idx]}])
            #                     print('train_data', train_data[0][cv_idx])
            dummy_ = [train_data[cv_idx][1]['entities'].append(i) for i in location_idx[cv_idx]]
            dummy = [train_data[cv_idx][1]['entities'].append(i) for i in skill_idx[cv_idx]]
            # print('train_data value is:', train_data[cv_idx][1])
            text_data.append([name, mb_nmb, email_, location, exp, skill])

            return train_data, text_data
        else:
            return 'No data', 'No data'
    else:
        return 'No data', 'No data'



    
def build_spacy_model(train, model=None):
    import warnings
    import random
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")

    TRAIN_DATA = train
    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    else:
        ner = nlp.get_pipe("ner")

    # add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
#             print(ent[2])
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes), warnings.catch_warnings():  # only train NER
        warnings.filterwarnings("ignore", category=UserWarning, module="spacy")
        if model is None:
            optimizer = nlp.begin_training()
        else:
            optimizer = nlp.resume_training()
        for itn in range(1):
            # train for 50 iteration
            print("Starting iteration " + str(itn))
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                try:
                    nlp.update(
                        [text],  # batch of texts
                        [annotations],  # batch of annotations
                        drop=0.2,  # dropout - make it harder to memorise data
                        sgd=optimizer,  # callable to update weights
                        losses=losses,
                    )
                except Exception as e:
                    pass
            print(losses)
            # plt.scatter(itn, losses["ner"])
            # plt.ylabel("ner_loss")
            # plt.xlabel("Iterations")
            # plt.show()

    nlp.to_disk(r"C:\Users\SPSOFT\Desktop\Latest_RMS\Resume management tool\v2.0\model\nlp_10112022")
    # plt.savefig("loss.png")
    return nlp

# In[ ]:


def word_2_pdf(file_path, file_name, new_file_name):
    import time
    # print('calling word_2_pdf function................')
    word = win32com.client.Dispatch('Word.Application',pythoncom.CoInitialize())
    word.Visible = False
    doc = word.Documents.Open(file_path+"\\"+file_name)
    # print('file location:', file_path+"\\"+file_name)
    time.sleep(5)
    doc.SaveAs(os.path.join(file_path,new_file_name), FileFormat=wdFormatPDF)
    # print('\nconversion:done..................')
    doc.Close()
    word.Quit()
    word.Visible = True


# In[ ]:


def resume_parser_trainer_(folder_):
    main_path = r"C:\Users\SPSOFT\Desktop\Latest_RMS\Resume management tool\v2.0\main"
    temp_path = r"C:\Users\SPSOFT\Desktop\Latest_RMS\Resume management tool\v2.0\temp"
    archieve_path = r"C:\Users\SPSOFT\Desktop\Latest_RMS\Resume management tool\v2.0\archieve"
    issue_path = r"C:\Users\SPSOFT\Desktop\Latest_RMS\Resume management tool\v2.0\archieve\unprocessed"
    resume_list = []
    model_train_data = []
    model_text_data = []
    folder_splt = folder_.split('_')
    model_req = []
    try:
        if folder_ in os.listdir(main_path):
            # print('folder found \n')
            shutil.move(main_path+'\\'+folder_, temp_path)
            file_path = os.path.join(temp_path,folder_)
            file_path_dir = os.listdir(temp_path+'\\'+folder_)
            # print('NO of files:', len(file_path_dir))
            if len(file_path_dir) > 0:
                # print('file greater than 0 condition')
                if folder_ in os.listdir(temp_path):
                    for file in file_path_dir:
                        print('file is:', file)
                        try:
                            flag_ = 0
                            resume_dic = {}
                            resume_dic['flag'] = flag_
                            resume_dic['createdOn'] = folder_splt[0]
                            resume_dic['createdBy'] = folder_splt[1]
                            ext = os.path.splitext(file)[1]
                            # print('not archieve folder condtion')
                            if ext.lower() in (".doc",".docx"):
                                try:
                                    # print("entered into try block")
                                    file_name = os.path.splitext(file)[0]
                                    if file_name.find("."):
                                        new_file_name = file_name.replace(".","_").strip()    
                                    else:
                                        new_file_name = file_name.strip()
                                    word_2_pdf(file_path, file, new_file_name)
                                    if os.path.exists(os.path.join(file_path, new_file_name+'.pdf')):
                                        trn_data, txt_data = single_file_pdfannotator(temp_path,folder_,new_file_name+'.pdf')
                                        os.remove(os.path.join(file_path, new_file_name+'.pdf'))
                                        mb_tst_ = txt_data[0][1]
                                        em_tst_ = txt_data[0][2]
                                        exp_tst_ = txt_data[0][4]
                                        name_tst_ = txt_data[0][0]
                                        loc_tst_ = txt_data[0][3][0]
                                        skill_tst_ = txt_data[0][5][0]
                                        if ('year' in exp_tst_.lower()) or ('yrs' in exp_tst_.lower()):
                                            exp_check = float(''.join([i for i in exp_tst_ if i.isnumeric() or i == '.']))
                                        else:
                                            exp_check = '-'
                                        if mb_tst_ == '-' or em_tst_ == '-' or exp_check == '-' or name_tst_ == '-' or loc_tst_ == '-' or skill_tst_[0] == '-':
                                            flag_ = 0
                                            if txt_data[0][0] == 'No pages':
                                                trn_data = 'Not pdf'
                                            # try:
                                            #     os.mkdir(issue_path+"\\"+folder_)
                                            #     shutil.move(file_path+"\\"+file, issue_path+"\\"+folder_)
                                            # except FileExistsError:
                                            #     shutil.move(file_path+"\\"+file, issue_path+"\\"+folder_)
                                        else:
                                            flag_ = 1
                                            # try:
                                            #     os.mkdir(archieve_path+"\\"+folder_)
                                            #     shutil.move(file_path+"\\"+file, archieve_path+"\\"+folder_)
                                            # except FileExistsError:
                                            #     shutil.move(file_path+"\\"+file, archieve_path+"\\"+folder_)
        
                                    else:
                                        # print('word file not converted to pdf...')
                                        flag_ = 0
                                        trn_data = 'Not pdf'
                                        try:
                                            os.mkdir(issue_path+"\\"+folder_)
                                            shutil.move(file_path+"\\"+file, issue_path+"\\"+folder_)
                                        except FileExistsError:
                                            shutil.move(file_path+"\\"+file, issue_path+"\\"+folder_)
                                        # continue
                                except Exception as err:
                                    # print('Error:', err)
                                    # print("entered into except block")
                                    # print('word file not converted to pdf...')
                                    flag_ = 0
                                    trn_data = 'Not pdf'
                                    try:
                                        os.mkdir(issue_path+"\\"+folder_)
                                        shutil.move(file_path+"\\"+file, issue_path+"\\"+folder_)
                                    except FileExistsError:
                                        shutil.move(file_path+"\\"+file, issue_path+"\\"+folder_)
                            elif ext.lower() == '.pdf':
                                trn_data, txt_data = single_file_pdfannotator(temp_path,folder_,file)
                                mb_tst_ = txt_data[0][1]
                                mb_tst_ = txt_data[0][1]
                                em_tst_ = txt_data[0][2]
                                exp_tst_ = txt_data[0][4]
                                name_tst_ = txt_data[0][0]
                                loc_tst_ = txt_data[0][3][0]
                                skill_tst_ = txt_data[0][5][0]
                                if ('year' in exp_tst_.lower()) or ('yrs' in exp_tst_.lower()):
                                    exp_check = float(''.join([i for i in exp_tst_ if i.isnumeric() or i == '.']))
                                else:
                                    exp_check = '-'
                                if mb_tst_ == '-' or em_tst_ == '-' or exp_check == '-' or name_tst_ == '-' or loc_tst_ == '-' or skill_tst_[0] == '-':
                                    flag_ = 0
                                    # trn_data = 'Not pdf'
                                    # try:
                                    #     os.mkdir(issue_path+"\\"+folder_)
                                    #     shutil.move(file_path+"\\"+file, issue_path+"\\"+folder_)
                                    # except FileExistsError:
                                    #     shutil.move(file_path+"\\"+file, issue_path+"\\"+folder_)
                                else:
                                    flag_ = 1
                                    # try:
                                    #     os.mkdir(archieve_path+"\\"+folder_)
                                    #     shutil.move(file_path+"\\"+file, archieve_path+"\\"+folder_)
                                    # except FileExistsError:
                                    #     shutil.move(file_path+"\\"+file, archieve_path+"\\"+folder_)
                            else:
                                flag_ = 0
                                trn_data = 'Not pdf'
                                # try:
                                #     os.mkdir(issue_path+"\\"+folder_)
                                #     shutil.move(file_path+"\\"+file, issue_path+"\\"+folder_)
                                    
                                # except FileExistsError:
                                #     shutil.move(file_path+"\\"+file, issue_path+"\\"+folder_)
                                   
        
                            if trn_data == 'Not pdf':
                                # print('issue condition')
                                resume_dic['filePath'] = issue_path+"\\"+folder_
                                resume_dic['fileName'] = file
                                
                                resume_dic['name'] = ''.join([i for i in file[:file.find([j for j in file if not (j.isalpha() or j.isspace())][0])] if i.isalpha() or i.isspace()])
                                
                                resume_dic['mobile'] = '-'
                                resume_dic['emailId'] = '-'
                                resume_dic['location'] = '-'
                                resume_dic['experience'] = 0.0
                                resume_dic['skills'] = '-'
                                resume_dic['flag'] = flag_
                                
                                ################# mongo insert
                                #mongo_insert([resume_dic])
        
                                resume_list.append(resume_dic)
            #                     continue
                            else:
                                # print('resume ok condition')
                                model_text_data.append(txt_data[0])
                                model_train_data.append(trn_data[0])
                                resume_dic['flag'] = flag_
                                if resume_dic['flag'] == 1:
                                    resume_dic['filePath'] = archieve_path+"\\"+folder_
                                    #model_path = r'E:\17112022\model\nlp_10112022'
                                    # print('file is:', file)
                                    # print('text data is:', txt_data)
                                    # build_spacy_model([trn_data[0]], model_path)
                                    
                                else:
                                    # print('file not trained:', file)
                                    # print('text data is:', txt_data)
                                    resume_dic['filePath'] = issue_path+"\\"+folder_         
                                resume_dic['fileName'] = file
                                
                                resume_dic['name'] = txt_data[0][0]
                                resume_dic['mobile'] = txt_data[0][1]
                                resume_dic['emailId'] = txt_data[0][2]
                                resume_dic['location'] = txt_data[0][3][0]
                                resume_dic['experience'] = exp_check
                                resume_dic['skills'] = txt_data[0][5][0]
                                model_req.append(resume_dic)
                            ################# mongo insert
                            #mongo_insert([resume_dic])
                        except Exception as err:
                            print('Error is: ', err)
                            continue
            else:
                pass
                                            
            # shutil.rmtree(temp_path+'\\'+folder_)
            return resume_list, model_train_data,model_text_data, model_req,list_city         
            
        else:
            print('Folder not found')
    except Exception as err:
        print('erro is:', err)
        pass
    
    


# In[ ]:


nlp = spacy.load('en_core_web_sm')



# In[ ]:


folder_ = '2022-11-29T10-50-30.559833200_7777'


# In[ ]:


# In[ ]:


#pd.DataFrame(rsm_lst)


# In[ ]:




# In[ ]:





# In[ ]:




# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




