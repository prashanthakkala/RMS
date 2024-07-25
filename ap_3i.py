from flask import Flask,jsonify,request,Response,json
import spacy
from Untitled7_ import build_spacy_model,resume_parser_trainer_,mongo_insert
import pandas as pd
import os
import shutil
import copy
from rms_features import Email
app = Flask(__name__)

#folder_="2022-08-22T09-51-27.349_1101"

model_path = r"C:\Users\SPSOFT\Desktop\Latest_RMS\Resume management tool\v2.0\model\nlp_10112022"
main_path = r"C:\Users\SPSOFT\Desktop\Latest_RMS\Resume management tool\v2.0\main"
temp_path = r"C:\Users\SPSOFT\Desktop\Latest_RMS\Resume management tool\v2.0\temp"
archieve_path = r"C:\Users\SPSOFT\Desktop\Latest_RMS\Resume management tool\v2.0\archieve"
issue_path = r"C:\Users\SPSOFT\Desktop\Latest_RMS\Resume management tool\v2.0\archieve\unprocessed"

tier_1 = ['delhi', 'mumbai', 'bangalore', 'chennai', 'hyderabad', 'kolkata', 'ahmedabad', 'pune', 'new delhi']               
tier_2 = ['agra', 'ajmer', 'aligarh', 'amravati', 'amritsar', 'anand', 'asansol', 'aurangabad', 'bareilly', 'belagavi', 'bhavnagar', 'bhilai', 'bhiwandi', 'bhopal', 'bhubaneswar', 'bikaner', 'bilaspur', 'bokaro-steel-city', 'chandigarh', 'coimbatore', 'cuttack', 'dehradun', 'dhanbad', 'durgapur', 'erode', 'faridabad', 'firozabad', 'ghaziabad', 'gorakhpur', 'guntur', 'gurugram', 'guwahati', 'gwalior', 'hamirpur', 'hubballi–dharwad', 'indore', 'jabalpur', 'jaipur', 'jalandhar', 'jalgaon', 'jammu', 'jamnagar', 'jamshedpur', 'jhansi', 'jodhpur', 'kakinada', 'kalaburagi', 'kannur', 'kanpur', 'karnal', 'kochi', 'kolhapur', 'kollam', 'kozhikode', 'kurnool', 'lucknow', 'ludhiana', 'madurai', 'malappuram', 'mangaluru', 'mathura', 'meerut', 'moradabad', 'mysuru', 'nagpur', 'nanded', 'nashik', 'nellore', 'noida', 'patna', 'prayagraj', 'puducherry', 'purulia', 'raipur', 'rajamahendravaram', 'rajkot', 'ranchi', 'ratlam', 'rourkela', 'salem', 'sangli', 'shimla', 'siliguri', 'solapur', 'srinagar', 'surat', 'thanjavur', 'thiruvananthapuram', 'thrissur', 'tiruchirappalli', 'tirunelveli', 'tiruvannamalai', 'ujjain', 'vadodara', 'varanasi', 'vasai-virar', 'vellore', 'vijayapura', 'vijayawada', 'visakhapatnam', 'warangal']
@app.route('/folder_path/<folder_>')
def rms_input_path(folder_):
    import copy
    global code_txt_data
    str_, txt_data, code_txt_data, result, list_city = resume_parser_trainer_(folder_)
    # print('list_city value is:', list_city)
    # print('--'*85)
    # print('\nstr_data is:', str_)
    # print('--'*85)
    # print('\ntxt_data is:', txt_data)
    # print('--'*85)
    # print('\ntext_data value is:\n', code_txt_data)
    model_input = copy.deepcopy(str_)
    for vlu in result:
        model_input.append(vlu)
    model_dump = [mongo_insert([result],'Mar_29_2024_model_before_training') for result in model_input]
    list_city = [i.lower() for i in list_city]
    str_copy = copy.deepcopy(str_)
    # print('len str_:', len(str_), 'len txt_data:', len(txt_data), 'len result:', len(result))
    model_result = []
    cnt = 0
    cnt_2 = 0
    flg_chk = [i for i in str_copy if i['flag'] == 0]
    # print(txt_data)
    # nlp_test = build_spacy_model(txt_data, model_path)
    # [build_spacy_model([txt_data[i]], model_path) for i in range(len(txt_data)) if result[i]['flag'] == 1]
    # print('result input:', result)
    # print('flg_chk value is:', flg_chk)
    
    # nlp_test = build_spacy_model(txt_data, model_path)
    nlp_test = spacy.load(model_path)
    for idx in range(len(str_)+len(result)):
        # print('\n')
        # print('loop length:', len(str_)+len(result))
        # print('\n')
        if idx < len(result):
            doc = nlp_test(txt_data[idx][0])
            name = []
            exp = []
            email = []
            mob = []
            locations = []
            skills = []
            dup_skill = []
            for ents in doc.ents:
                if ents.label_ == 'NAME':
                    name.append(ents.text)
                elif ents.label_ == 'EXPERIENCE':
                    # print('**'*85)
                    # print('experience value is:', ents.text)
                    # print('**'*85)
                    if ('year' in ents.text) or ('yrs' in ents.text):
                        cnt_spc = 0
                        exp_num_ = []
                        for vlu in ents.text:
                            if vlu.isnumeric():
                                exp_num_.append(vlu)
                            elif vlu == '.' and cnt_spc == 0 and len(exp_num_) > 0:
                                cnt_spc = 1
                                exp_num_.append(vlu)
                        # print('exp_num value is:', exp_num_)
                        if len(exp_num_) > 0:
                            exp_num = float(''.join(exp_num_))
                            exp.append(exp_num)
                        
                elif ents.label_ == 'EMAIL':
                    email.append(ents.text)
                elif ents.label_ == 'MOBILE':
                    mob.append(ents.text)   
                elif ents.label_ == 'SKILL':
                    skill_text = ents.text.lower()
                    if ('year' in skill_text) or ('yrs' in skill_text) \
                        or (skill_text in dup_skill) or (skill_text in skills):
                        continue
                    else:
                        skills.append(skill_text)
                        dup_skill.append(''.join(skill_text.split()))
                elif ents.label_ == 'LOCATION':
                    locations.append(ents.text)
                    
            code_location_match = code_txt_data[idx][3][0]
            if len(locations) > 0:
                location_match = [loc.lower() for loc in locations if loc.lower() in list_city]
                if len(location_match) > 0:
                    tier_1_match = [i.lower() for i in location_match if i.lower() in tier_1]
                    tier_2_match = [i.lower() for i in location_match if i.lower() in tier_2]
                    if len(tier_1_match) > 0:
                        result[cnt]['location'] = ','.join(list(set(tier_1_match)))
                    elif len(tier_1_match) > 0:
                        result[cnt]['location'] = ','.join(list(set(tier_2_match)))
                    else:
                        result[cnt]['location'] = ','.join(list(set(location_match)))
                else:
                    result[cnt]['location'] = '-'
            elif len(locations) == 0 and len(code_location_match) > 2:
                location_match = []
                # result[cnt]['location'] = '---'
                result[cnt]['location'] = code_location_match
            else:
                location_match = []
                result[cnt]['location'] = 'India'
            code_name_match = code_txt_data[idx][0]    
            if len(name) > 0:
                # print('name values are:', name)
                stp_wrds = ['address', 'mail', 'email','hno', 'contact', 'mobile', 'test', 'engineer',
                            'qa', 'senior', 'software', 'developer', 'data', 'analyst', 'summary','Informatica',
                            'career', 'phone', 'cell', 'associate','aws', 'salesforce', 'india', 'curriculum','experienced','no','trained','technical','curriculam','vitae',
                            'validation', 'sheet', 'azure', 'devops', 'personal', 'profile', 'professional', 'experience']
                name_ = name[0].lower().replace('resume', '').replace('name','').strip()
                name_ = ''.join([i for i in name_ if i.isalpha() or i.isspace() or i == '.'])
                name_ = ' '.join([i for i in name_.split(' ') if i.replace('.','').strip().lower()
                                  not in location_match and i.replace('.','').replace(' ','').lower().strip() not in stp_wrds and 'mail' not in i])
                result[cnt]['name'] = name_
                if (len(name_) < 3) or (name_ == 'Not Matched') or (name_.lower() == 'contact'):
                    result[cnt]['name'] = '-'
                elif len(name_.split()) > 3:
                    name_1 = ' '.join(name_.split()[:3])
                    if len(name_1.replace(' ','').strip()) > 3:
                        result[cnt]['name'] = name_1
                    elif len(name_1.replace(' ','').strip()) < 3 and \
                        len(name_.replace(' ','').strip()) >=3:
                        result[cnt]['name'] = name_
                    else:
                        result[cnt]['name'] = '-'
            elif len(name) == 0 and len(code_name_match) > 2:
                # result[cnt]['name'] = '---'
                result[cnt]['name'] = code_name_match
            else:
                result[cnt]['name'] = '-'
            
            
            code_email_match = code_txt_data[idx][2]
            if len(email) > 0:
                email_instance = Email(email[0])
                mail = email_instance.extractor()[0]
                if len(mail) > 2:
                    result[cnt]['emailId'] = mail
                elif len(email) <= 2 and len(code_email_match) > 2:
                    # result[cnt]['emailId'] = '---'
                    result[cnt]['emailId'] = code_email_match
                # mail_= email[0].lower().replace('Email:','').replace('mail:','').replace('E-','').strip()
                # result[cnt]['emailId'] = mail_
                # if '@' in mail_:
                #     if ('.com' not in email[0]) or ('.in' not in email[0]):
                #         result[cnt]['emailId'] = mail_
                #     else:
                #         result[cnt]['emailId'] = '-'
                else:
                    result[cnt]['emailId'] = '-'
            elif len(email) == 0 and len(code_email_match) > 2:
                # result[cnt]['emailId'] = '---'
                result[cnt]['emailId'] = code_email_match
            else:
                result[cnt]['emailId'] = '-'
            
            code_mob_match = [i for i in code_txt_data[idx][1] if i.isnumeric()]
            if len(mob) > 0:
                result[cnt]['mobile'] = mob[0]
                mob_check = [i for i in mob[0] if i.isnumeric()]
                if len(mob_check) < 10:
                    result[cnt]['mobile'] = '-'
                elif len(mob_check) >= 10:
                    mob_reduce = ''.join(mob_check[-10:])
                    result[cnt]['mobile'] = mob_reduce
            elif len(mob) == 0 and len(code_mob_match) > 2:
                # result[cnt]['mobile'] = '---'
                if len(code_mob_match) >= 10:
                    code_mob_match_ = ''.join(code_mob_match[-10:])
                    result[cnt]['mobile'] = code_mob_match_
                else:
                    result[cnt]['mobile'] = '-'
            else:
                result[cnt]['mobile'] = '-'
            code_exp_match = code_txt_data[idx][4]
            if len(exp) > 0:
                result[cnt]['experience'] = exp[0]
            elif len(exp) == 0 and len(code_exp_match) > 2:
                if ('year' in code_exp_match) or ('yrs' in code_exp_match):
                    cnt_spc = 0
                    exp_num_2 = []
                    for vlu in code_exp_match:
                        if vlu.isnumeric():
                            exp_num_2.append(vlu)
                        elif vlu == '.' and cnt_spc == 0 and len(exp_num_2) > 0:
                            cnt_spc = 1
                            exp_num_2.append(vlu)
                    # print('exp_num value is:', exp_num_)
                    if len(exp_num_2) > 0:
                        result[cnt]['experience'] = float(''.join(exp_num_2))
                    else:
                        result[cnt]['experience'] = 0
                else:
                    result[cnt]['experience'] = 0
            else:
                result[cnt]['experience'] = 0
            if len(skills) > 0:
                out_skills = list(set([i.lower() for i in list(set(skills))]))
                out_skills = [i.lower() for i in out_skills if i.lower() not in list_city]
                result[cnt]['skills'] = out_skills
            else:
                result[cnt]['skills'] = ['-']
            
            
                
            # if result[cnt]['name'] == '-' or  result[cnt]['experience'] == 0 or result[cnt]['skills'] == ['-'] or result[cnt]['location'] == '---' or result[cnt]['name'] == '---':
            if result[cnt]['name'] == '-' or  result[cnt]['experience'] == 0 or result[cnt]['skills'] == ['-']:
                result[cnt]['flag'] = 0
                
                file_name = result[cnt]['fileName']
                result[cnt]['filePath'] = issue_path+"\\"+folder_
                
                # print('dic file name is:', result[cnt]['fileName'])
                # print('file_name value in if is:', file_name)
                if os.path.exists(os.path.join(temp_path+"\\"+folder_, file_name)): 
                    try:
                        os.mkdir(issue_path+"\\"+folder_)
                        shutil.move(temp_path+"\\"+folder_+"\\"+file_name, issue_path+"\\"+folder_)
                        
                    except FileExistsError:
                        shutil.move(temp_path+"\\"+folder_+"\\"+file_name, issue_path+"\\"+folder_)
                else:
                    pass
                # print('result value in flag 0 cond:', result[cnt])
                    
            else:
                no_value = ['-', '---']
                if result[cnt]['mobile'] in no_value and result[cnt]['emailId'] in no_value:
                    print('\nfile_name:', result[cnt]['fileName'])
                    result[cnt]['flag'] = 0
                    
                    file_name = result[cnt]['fileName']
                    result[cnt]['filePath'] = issue_path+"\\"+folder_
                    
                    # print('dic file name is:', result[cnt]['fileName'])
                    # print('file_name value in if is:', file_name)
                    if os.path.exists(os.path.join(temp_path+"\\"+folder_, file_name)): 
                        try:
                            os.mkdir(issue_path+"\\"+folder_)
                            shutil.move(temp_path+"\\"+folder_+"\\"+file_name, issue_path+"\\"+folder_)
                            
                        except FileExistsError:
                            shutil.move(temp_path+"\\"+folder_+"\\"+file_name, issue_path+"\\"+folder_)
                    else:
                        pass
                else:
                    result[cnt]['flag'] = 1
                    file_name = result[cnt]['fileName']
                    result[cnt]['filePath'] = archieve_path+"\\"+folder_
                    
                    # print('dic file name is:', result[cnt]['fileName'])
                    # print('file_name value in if is:', file_name)
                    if os.path.exists(os.path.join(temp_path+"\\"+folder_, file_name)): 
                        try:
                            os.mkdir(archieve_path+"\\"+folder_)
                            shutil.move(temp_path+"\\"+folder_+"\\"+file_name, archieve_path+"\\"+folder_)
                            
                        except FileExistsError:
                            shutil.move(temp_path+"\\"+folder_+"\\"+file_name, archieve_path+"\\"+folder_)
                    else:
                        pass
            # print('result value in flag 0 cond:', result[cnt])
            model_result.append(result[cnt])
            mongo_insert([result[cnt]],'Mar_29_2024_collection_after_training')
            cnt += 1
            
        else:
            # flg_chk[cnt_2]
            model_result.append(flg_chk[cnt_2])
            # print('flg_chk value is:', flg_chk[cnt_2])
            mongo_insert([flg_chk[cnt_2]],'Mar_29_2024_collection_after_training')
            
            file_name = flg_chk[cnt_2]['fileName']
            flg_chk[cnt_2]['filePath'] = issue_path+"\\"+folder_
            if os.path.exists(os.path.join(temp_path+"\\"+folder_, file_name)): 
                try:
                    os.mkdir(issue_path+"\\"+folder_)
                    shutil.move(temp_path+"\\"+folder_+"\\"+file_name, issue_path+"\\"+folder_)
                    
                except FileExistsError:
                    shutil.move(temp_path+"\\"+folder_+"\\"+file_name, issue_path+"\\"+folder_)
            else:
                pass

            cnt_2 += 1
            
        folder_len = len(os.listdir(temp_path+"\\"+folder_))
        # print('model_result value is:', len(model_result))
        if folder_len == 0:
            shutil.rmtree(temp_path+'\\'+folder_)
            break
        
        
    # print("Model_result value is:", model_result) 
    # print('-'*85)

    return "Compleeeeeettted"


@app.route('/add_sum/<x>')
def add_sum(x):
    # print(type(x))
    y=int(x)+10000
    # print(y)
    return "commmmmplted"




#14.142.118.7 
if __name__ == '__main__':
     app.run('0.0.0.0',debug=False,port ="8999")
 #      app.run('192.168.35.216',debug=False,port ="8999")