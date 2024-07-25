import re



class Email:
    def __init__(self, data):
        self.data = data
            
    def _annotator(self, email_):
        start_idx = self.data.find(email_)
        end_idx = start_idx + len(email_)
        annotation = [start_idx, end_idx, 'EMAIL']
        return annotation
    
    def extractor(self):
        email_ = re.findall(re.compile(r'[A-Za-z0-9_.]+[\s]?[@](?:[a-zA-Z]{4,})[\s]?(?:[.a-zA-Z]{2,4})?'), self.data)
        email_ = list(set(email_))
        if email_:
            email_ = email_[0]
            annotation = self._annotator(email_)
    
            return email_, annotation
        else:
            return '-', [-1,0,'UNLABELED']
        
        
class Mobile_number:
    def __init__(self, data):
        self.data = data
            
    def _annotator(self, mobile_num):
        start_idx = self.data.find(mobile_num)
        end_idx = start_idx + len(mobile_num)
        annotation = [start_idx, end_idx, "MOBILE"]
        return annotation
    
    def extractor(self):
        mobile_num_lst = re.findall(re.compile(r'[6-9]{1}[\d]{9,}|[6-9]{1}[\d]{4}[( -.][\d]{5}|[(]?[6-9]{1}[\d]{2}[( -.]+[\d]{3}[( -.]+[\d]{4}|[(]?[6-9]{1}[\d]{3}[( -.]+[\d]{3}[( -.]+[\d]{3}|[(]?[6-9]{1}[\d]{2}[( -.]+[\d]{4}[( -.]+[\d]{3}|[(]?[6-9]{1}[\d]{1}[( -.]+[\d]{2}[( -.]+[\d]{2}[( -.][\d]{2}[( -.][\d]{2}|[(]?[6-9]{1}[( -.]+[\d]{1}[( -.]+[\d]{1}[( -.]+[\d]{1}[( -.]+[\d]{1}[( -.]+[\d]{1}[( -.]+[\d]{1}[( -.]+[\d]{1}[( -.]+[\d]{1}[( -.][\d]{1}|[(]?[6-9]{1}[\d]{5}[( -.]+[\d]{4}|[(]?[6-9]{1}[\d]{3}[( -.]+[\d]{6}|[(]?[6-9]{1}[\d]{1}[( -.]+[\d]{4}[( -.]+[\d]{4}'), 
                                    self.data)
        if mobile_num_lst:
            processed_mobile_num = ''
            mobile_num = mobile_num_lst[0]
            for char in mobile_num:
                if char.isnumeric() or char in ('-', '.', ' ', '(', ')'):
                    processed_mobile_num += str(char)
            if len(processed_mobile_num) == 10:
                annotation = self._annotator(mobile_num)
                return processed_mobile_num, annotation
            elif len(processed_mobile_num) == 12:
                processed_mobile_num = processed_mobile_num[-10:]
                annotation = self._annotator(mobile_num)
                return processed_mobile_num, annotation
            else:
                return '-', [-1, 0, "UNLABELED"]
        else:
            return '-', [-1, 0, "UNLABELED"]
        
    
class Experience:
    def __init__(self, data):
        self.data = data

    def _annotator(self, exp):
        start_idx = self.data.find(exp)
        end_idx = start_idx + len(exp)
        annotation = [start_idx, end_idx, 'EXPERIENCE']
        return annotation

    def extractor(self):
        text = self.data.lower()
        pattern = re.compile(r'[0-9.]{1,4}[\s]*?[\s+]*?[\s]?(?:years?|yrs?|months?)',re.I)
        pattern1 = re.compile(r'\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4}[\s]?(?:to|-|till)[\s]?\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4}',re.I)
        pattern2 = re.compile(r'\d{1,4}[\/-]\d{1,2}[\/-]\d{2,4}[\s]?(?:to|-|till)[\s]?(?:till|present|current)',re.I)
        pattern3 = re.compile(r'[a-zA-Z]+[\'-\\\/\s]?[\d]{4}[\s-]?(?:to|-|till|to till)?[\s]?(?:till date|present|current|till now)',re.I)
        pattern4 = re.compile(r'[a-zA-Z]+[\'-\\\/\s]?[\d]{4}[\s-]?(?:to|-|till|to till)?[\s-]?[a-zA-Z]+[\'-\\\/\s]?[\d]{4}',re.I)
        pattern5 =  re.compile(r'[a-zA-Z]+[\'-\\\/\s]?[\d]{1,2}[\'-\\\/\s]?[\d]{4}[\s-]?(?:to|-|till|to till)?[\s-]?[a-zA-Z]+[\'-\\\/\s]?[\d]{1,2}[\'-\\\/\s]?[\d]{4}',re.I)
        res = re.findall(pattern,text)
        result = [vlu for vlu in res if vlu.strip()[0]]
        result1 = result2 = []
        if len(result) == 0:
    #         print('result')
            res1 = re.findall(pattern1, text)
    #         result1 = [vlu for vlu in res1 if vlu.strip()[0].isnumeric()]
            result1 = [vlu for vlu in res1 if vlu.strip()[0]]
    #         print(result1)
            if len(result1) == 0:
                result1 = None
            else:
                annotation = self._annotator(result1[0])
                return result1[0], annotation
        else:
            annotation = self._annotator(result[0])
            return result[0], annotation
        if result1 == None:
    #         print('result1')
            res2 = re.findall(pattern2, text)
            result2 = [vlu for vlu in res2 if vlu.strip()[0].isnumeric()]
    #         print(result2)
            if len(result2) == 0:
                result2 = None
            else:
                annotation = self._annotator(result2[0])
                return result2[0], annotation
        if result2 == None:
    #         print('result2')
            res3 = re.findall(pattern3, text)
        #     result3 = [vlu for vlu in res3 if vlu.strip()[0].isnumeric()]
    #         print(res3)
            if len(res3) == 0:
                result3 = None
    #             return 'Not found', [-1, 0, 'UNLABELED']
            else:
                annotation = self._annotator(res3[0])
                return res3[0], annotation
        if result3 == None:
            res4 = re.findall(pattern4, text)
            if len(res4) == 0:
                result4 = None
            else:
                annotation = self._annotator(res4[0])
                return res4[0], annotation
        if result4 == None:
            res5 = re.findall(pattern5, text)
            if len(res5) == 0:
                return '-', [-1, 0, 'UNLABELED']
            else:
                annotation = self._annotator(res5[0])
                return res5[0], annotation
        
        



