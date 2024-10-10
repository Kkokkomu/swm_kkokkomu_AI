import re
import base64
from PIL import Image
from io import BytesIO
import os
import json


def sanitize_filename(filename):
    
    # 사용할 수 없는 문자 목록: \ / : * ? " < > |
    unsafe_characters = r'[:*?"<>|]'
    # 사용할 수 없는 문자를 '_'로 대체
    return re.sub(unsafe_characters, '_', filename)




def SaveImg(response, path ='./image.png'):
    
    # Base64 문자열 디코딩
    image_data = base64.b64decode(response)

    image = Image.open(BytesIO(image_data))

    image.save(path, "PNG")


def saveJsonFile(path, crawl, title, summary, keywords, characters):
    data ={'url' : crawl['url'], 'title' : title, 'summary':summary ,'section' : crawl['section'], 
           'keywords' : {f'keyword_{i}' : keyword.strip() for i, keyword in enumerate(keywords.split(','))},'characters' :characters}

    titleForPath = sanitize_filename(title)
    title_path = path + '/'+ titleForPath
    if not os.path.isdir(title_path):
        os.makedirs(title_path)

    with open(title_path +'/data.json','w', encoding='UTF-8') as json_file:
        json.dump(data, json_file,indent='\t',ensure_ascii=False)
    
    return title_path

def saveTTS(tts, title_path):
    for i,t in enumerate(tts):
        t.stream_to_file(title_path+f'/sentence_{i}.wav')
