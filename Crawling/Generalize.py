import pickle
import urllib3
import json
import re

with open('./secret.json') as f:
    secrets = json.loads(f.read())
    
SECRET_KEY = secrets['NER_API']

with open('user.pkl', 'rb') as fr:
    change_words = pickle.load(fr)
    
openApiURL = "http://aiopen.etri.re.kr:8000/WiseNLU" 
    
accessKey = SECRET_KEY
analysisCode = "ner"


def Generalize(text):

    requestJson = {  
        "argument": {
            "text": text,
            "analysis_code": analysisCode
        }
    }
        
    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        openApiURL,
        headers={"Content-Type": "application/json; charset=UTF-8", "Authorization" :  accessKey},
        body=json.dumps(requestJson)
    )
    string_data = response.data.decode('utf-8')

    # 2. 문자열을 JSON 객체로 변환
    json_data = json.loads(string_data)
    ner_data = json_data['return_object']['sentence'][0]['NE']
    result ={}
    for res in ner_data:

        for key in change_words:

            if len(key) == 2:
                if res['type'][:2] ==key:
                    result[res['text']] = change_words[key]
                    break
            else:
                if res['type']== key:
                    result[res['text']] = change_words[key]

                    break
    # 딕셔너리의 키를 정규표현식 패턴으로 만듭니다.
    pattern = re.compile("|".join(re.escape(key) for key in result.keys()))

    # 패턴에 맞는 부분을 딕셔너리의 값으로 바꾸는 함수
    def replace_match(match):
        return result[match.group(0)]

    # 문장 변환
    result = pattern.sub(replace_match, text)

    return result

if __name__ =='__main__':
    text = "곽상언 의원은 쌍방울 대북송금 사건을 수사한 검사 1명에 대한 탄핵소추안 법사위 회부에 기권표를 던지며 당내 비판을 받고 있습니다."
    print(Generalize(text))


