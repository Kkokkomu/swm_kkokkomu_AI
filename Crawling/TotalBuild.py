import EntertainCrawling, NewsCrawling, SportsCrawling
import Generate
from datetime import datetime
import os
import json
from tqdm import tqdm
from SaveFiles import SaveImg, saveJsonFile, saveTTS, sanitize_filename, saveTxT
from ImgGenerator import connectWebui, ImgGenerator
from RSS import findTopNews,findNewsContents

import subprocess


def renewalMakeComponent(count_news = 5, count_sports = 5, count_entertain = 5, path = ''):
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

            
            title, summary, keywords, characters= Generate.makeJson(content)
            

            title_path = saveJsonFile(section_path, crawl, title, summary,keywords, characters)

            title_path = './Data'
            saveTxT(title_path, summary)

            try:
                tts = [Generate.generate_TTS_clova(summary[f'Pronounce_{idx}']) for idx in range(3)]
                saveTTS(tts, title_path)

            except:
                print('GPT API로 TTS 제작')
                tts = [Generate.generate_TTS(summary[f'Pronounce_{idx}']) for idx in range(3)]
                saveTTS(tts, title_path)


            subprocess.call(f"mfa align --clean --overwrite --output_format json {title_path} korean_mfa korean_mfa {title_path}")
            
            try:
                images = connectWebui(summary['prompt_total'])

                for idx, image in enumerate(images):
                    SaveImg(image, path = title_path+f'/sentence_{idx}.png')

            
            except:
                print("\nGetImg로 이미지를 생성합니다.\n")
                for idx in range(3):
                    image = ImgGenerator(summary[f'Prompt{idx}'])
                    SaveImg(image, path = title_path+f'/sentence_{idx}.png')
        

def newsis_Make(headline =7, politic =7, world = 7, economy = 7 , IT = 7 , society = 7 , sports = 7, entertain = 7,culture =7):

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

    news_set =findTopNews(headline, politic, world, economy, IT, society, sports, entertain, culture)
    
    crawls = findNewsContents(news_set)

    for crawl in tqdm(crawls, desc = '뉴스 재료 생성 중'):
        section_path = path+'/'+ crawl['section']
    
        if not os.path.isdir(section_path):
            os.makedirs(section_path)

        content = '\n'.join(crawl['content'])

        
        title, summary, keywords, characters= Generate.makeJson(content)
        

        title_path = saveJsonFile(section_path, crawl, title, summary,keywords, characters)

        # title_path = './Data'
        saveTxT(title_path, summary)

        try:
            tts = [Generate.generate_TTS_clova(summary[f'Pronounce_{idx}']) for idx in range(3)]
            saveTTS(tts, title_path)

        except:
            print('GPT API로 TTS 제작')
            tts = [Generate.generate_TTS(summary[f'Pronounce_{idx}']) for idx in range(3)]
            saveTTS(tts, title_path)


        # subprocess.call(f"mfa align --clean --overwrite --output_format json {title_path} korean_mfa korean_mfa {title_path}")
        
        try:
            images = connectWebui(summary['prompt_total'])

            for idx, image in enumerate(images):
                SaveImg(image, path = title_path+f'/sentence_{idx}.png')

        
        except:
            print("\nGetImg로 이미지를 생성합니다.\n")
            for idx in range(3):
                image = ImgGenerator(summary[f'Prompt{idx}'])
                SaveImg(image, path = title_path+f'/sentence_{idx}.png')



if __name__ == '__main__':
    # 파라미터 주요뉴스 갯수, 스포츠 뉴스, 연예 뉴스 갯수
    # MakeSeperateComponent(1, 0, 0)
    # MakeJson(0,2,2)
    # renewalMakeComponent(0,1,0)

    newsis_Make(1,1,1,0,0,0,0,0)



    # with open('./resource/data.json', 'r', encoding='UTF-8') as json_file:
    #     data_content = json.load(json_file)
    # summary = data_content['summary']['prompt_total']
    # images = connectWebui(summary)

    # for idx, image in enumerate(images):
    #     SaveImg(image, path = f'./resource/sentence_{idx}.png')
