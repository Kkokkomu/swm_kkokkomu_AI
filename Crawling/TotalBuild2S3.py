import EntertainCrawling, NewsCrawling, SportsCrawling
import Generate
from datetime import datetime
import Video
import json
import boto3
from pydantic import BaseModel
from tqdm import tqdm
from ImgGenerator import SaveImg

import re

with open('./secret.json') as f:
    secrets = json.loads(f.read())
    
# AWS S3 설정
AWS_ACCESS_KEY_ID = secrets['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = secrets['AWS_SECRET_ACCESS_KEY']
AWS_REGION = secrets['AWS_REGION']
BUCKET_NAME = secrets['BUCKET_NAME']

# S3 클라이언트 생성
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

# S3에 객체 업로드 하는 함수
def save_to_s3(file_path, bucket_name, s3_key):
    try:
        s3_client.upload_file(file_path, bucket_name, s3_key)
        print(f"File {file_path} uploaded to S3 as {s3_key}.")
    except Exception as e:
        print(f"Failed to upload {file_path} to S3: {e}")
        return None
    return f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

def SaveSeperateData(path, crawl, title, summary, keywords ,tts, images = None):
    data ={'url' : crawl['url'], 'title' : title, 'summary':summary ,'section' : crawl['section'], 
           'keywords' : {f'keyword_{i}' : keyword.strip() for i, keyword in enumerate(keywords.split(','))}}

    title_path = path
    data_json_path = f"{title_path}/data.json"
    with open(data_json_path, 'w', encoding='UTF-8') as json_file:
        json.dump(data, json_file, indent='\t', ensure_ascii=False)

    for i, t in enumerate(tts):
        t.stream_to_file(f"{title_path}/sentence_{i}.wav")

    if images:
        for i, image in enumerate(images):
            SaveImg(image, path=f"{title_path}/sentence_{i}.png")

    return data_json_path

class ComponentRequest(BaseModel):
    id: int
    count_news : int
    count_sports : int 
    count_entertain : int

class ComponentResponse(BaseModel):
    data : dict
    s3 : str

# 크롤링, gpt 사용
def MakeSeperateComponent(request : ComponentRequest):
    path = './resource'

    kind_of_news = [NewsCrawling.News, SportsCrawling.sportsNews, EntertainCrawling.entertainNews ]
    
    counts = [request.count_news, request.count_sports, request.count_entertain]

    response = []
    for kind, count in zip(tqdm(kind_of_news, desc = '대분류 반복'),counts):
        crawls = kind(count)
        if not crawls:
            continue
        for crawl in tqdm(crawls,desc = '세부 내용 반복중'):
            content = '\n'.join(crawl['content'])
            title,summary, keywords,tts, images= Generate.SeperateSentence(content)
            json_path = SaveSeperateData(path, crawl, title, summary,keywords,tts, images)

            # data.json 파일 읽기
            with open(json_path, 'r', encoding='UTF-8') as json_file:
                data_content = json.load(json_file)

            # 비디오 생성 및 저장
            print(crawl['section'])
            video_path = f"{path}/final_output.mp4"
            Video.generate_video(crawl['section'])  
            
            # S3에 업로드
            url = save_to_s3(video_path, BUCKET_NAME, f"{request.id}.mp4")

            # 반환값
            response.append(ComponentResponse(data=data_content, s3=url))
    
    return response


if __name__ == '__main__':
    # MakeComponent(10,10,10)
    # 파라미터 주요뉴스 갯수, 스포츠 뉴스, 연예 뉴스 갯수
    MakeSeperateComponent(1, 0, 0)