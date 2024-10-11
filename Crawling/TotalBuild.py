import EntertainCrawling, NewsCrawling, SportsCrawling
import Generate
from datetime import datetime
import os
import json
from tqdm import tqdm
from ImgGenerator import SaveImg

import re


def sanitize_filename(filename):
    
    # 사용할 수 없는 문자 목록: \ / : * ? " < > |
    unsafe_characters = r'[:*?"<>|]'
    # 사용할 수 없는 문자를 '_'로 대체
    return re.sub(unsafe_characters, '_', filename)

def SaveSeperateData(path, crawl, title, summary, keywords ,tts, images = None):
    data ={'url' : crawl['url'], 'title' : title, 'summary':summary ,'section' : crawl['section'], 
           'keywords' : {f'keyword_{i}' : keyword.strip() for i, keyword in enumerate(keywords.split(','))}}

    titleForPath = sanitize_filename(title)
    title_path = path + '/'+ titleForPath
    if not os.path.isdir(title_path):
        os.makedirs(title_path)

    with open(title_path +'/data.json','w', encoding='UTF-8') as json_file:
        json.dump(data, json_file,indent='\t',ensure_ascii=False)

    # tts.astream_to_file(title_path+'/tts.mp3')
    for i,t in enumerate(tts):

        t.stream_to_file(title_path+f'/sentence_{i}.wav')
    if images:
        for i,image in enumerate(images):

            SaveImg(image, path = title_path+f'/sentence_{i}.png')
# 크롤링, gpt 사용


# 크롤링, gpt 사용
def MakeSeperateComponent(count_news = 5, count_sports = 5, count_entertain = 5, path = ''):
    kind_of_news = [NewsCrawling.News, SportsCrawling.sportsNews, EntertainCrawling.entertainNews ]
    
    counts = [count_news, count_sports, count_entertain]

    date = datetime.now().date()
    path = str(date)

    if not os.path.isdir(path):
        os.makedirs(path)

    time = datetime.now().strftime('%H-%M')
    path = path +'/' + time
    if not os.path.isdir(path):
        os.makedirs(path)
    else:
        print('같은 폴더가 존재합니다.')
        return
    # count가 0일 때 제외

    for kind, count in zip(tqdm(kind_of_news, desc = '대분류 반복'),counts):
        crawls = kind(count)
        if not crawls:
            continue
        for crawl in tqdm(crawls,desc = '세부 내용 반복중'):

            section_path = path+'/'+ crawl['section']
    
            if not os.path.isdir(section_path):
                os.makedirs(section_path)

            content = '\n'.join(crawl['content'])
            title, summary, keywords, tts, images= Generate.SeperateSentence(content)
            SaveSeperateData(section_path, crawl, title, summary,keywords,tts, images)


if __name__ == '__main__':
    # 파라미터 주요뉴스 갯수, 스포츠 뉴스, 연예 뉴스 갯수
    MakeSeperateComponent(2, 2, 2)