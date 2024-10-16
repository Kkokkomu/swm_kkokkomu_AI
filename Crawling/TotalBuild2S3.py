import EntertainCrawling, NewsCrawling, SportsCrawling
import Generate
from datetime import datetime
import Video
import json
import boto3
from pydantic import BaseModel
from tqdm import tqdm
from moviepy.editor import ImageClip
from SaveFiles import SaveImg, saveJsonFile, saveTTS
from ImgGenerator import connectWebui, ImgGenerator

import re

with open('./secret.json') as f:
    secrets = json.loads(f.read())
    
# AWS S3 설정
AWS_ACCESS_KEY_ID = secrets['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = secrets['AWS_SECRET_ACCESS_KEY']
AWS_REGION = secrets['AWS_REGION']
SHORTFORM_BUCKET_NAME = secrets['BUCKET_NAME']
WITHAD_BUCKET_NAME = secrets['WITHAD-BUCKET_NAME']
THUMBNAIL_BUCKET_NAME = "kkm-thumbnail"

# S3 클라이언트 생성
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

# 썸네일 이미지 조정
def adjust_thumbnail_to_9_16(image_path, output_path, target_width=180):
    # 9:16 비율 설정
    target_aspect_ratio = 9 / 16
    target_height = int(target_width / target_aspect_ratio)

    # 이미지 클립 생성
    clip = ImageClip(image_path)

    # 현재 이미지의 가로, 세로 비율 계산
    current_aspect_ratio = clip.w / clip.h

    # 이미지가 더 넓은 경우: 가로 크기를 유지하고 세로 여백만 추가
    new_width = target_width
    new_height = int(new_width / current_aspect_ratio)

    # 이미지 크기 조정
    clip = clip.resize(newsize=(new_width, new_height))

    # 위아래에 여백 추가 (이미지를 9:16 비율로 맞추기)
    clip = clip.on_color(size=(new_width, target_height), color=(0, 0, 0), pos=("center", "center"))

    # 이미지 저장
    clip.save_frame(output_path)

# S3에 객체 업로드 하는 함수
def save_to_s3(file_path, bucket_name, s3_key):
    try:
        s3_client.upload_file(file_path, bucket_name, s3_key)
        print(f"File {file_path} uploaded to S3 bucket {bucket_name} as {s3_key}.")
    except Exception as e:
        print(f"Failed to upload {file_path} to S3: {e}")
        return None
    return f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

# def SaveSeperateData(path, crawl, title, summary, keywords ,tts, images = None):
#     print('SaveSeperateData')
#     data ={'url' : crawl['url'], 'title' : title, 'summary':summary ,'section' : crawl['section'], 
#            'keywords' : {f'keyword_{i}' : keyword.strip() for i, keyword in enumerate(keywords.split(','))}}

#     title_path = path
#     data_json_path = f"{title_path}/data.json"
#     with open(data_json_path, 'w', encoding='UTF-8') as json_file:
#         json.dump(data, json_file, indent='\t', ensure_ascii=False)

#     for i, t in enumerate(tts):
#         with open(f"{title_path}/sentence_{i}.wav", 'wb') as audio_file:
#             audio_file.write(t)

#     if images:
#         for i, image in enumerate(images):
#             SaveImg(image, path=f"{title_path}/sentence_{i}.png")

#     return data_json_path

class ComponentRequest(BaseModel):
    id_list: list[int]
    count_news : int
    count_sports : int 
    count_entertain : int

class ComponentResponse(BaseModel):
    data : dict
    s3 : str
    thumbnail : str

# 크롤링, gpt 사용
def MakeSeperateComponent(request : ComponentRequest):
    path = './resource'

    kind_of_news = [NewsCrawling.News, SportsCrawling.sportsNews, EntertainCrawling.entertainNews ]
    
    counts = [request.count_news, request.count_sports, request.count_entertain]

    response = []
    id_list = request.id_list
    for i in id_list:
        print("id list " + str(i))
    id_idx = 0
    for kind, count in zip(tqdm(kind_of_news, desc = '대분류 반복'),counts):
        crawls = kind(count)
        if not crawls:
            continue
        for crawl in tqdm(crawls,desc = '세부 내용 반복중'):
            content = '\n'.join(crawl['content'])

            title, summary, keywords, characters= Generate.makeJson(content)
            title_path = saveJsonFile(path, crawl, title, summary,keywords, characters)

            json_path = f'{title_path}/data.json'

            tts = [Generate.generate_TTS_clova(summary[f'sentence_{idx}']) for idx in range(3)]
            saveTTS(tts, title_path)

            try:
                print("try connectWebui")
                images = connectWebui(summary['prompt_total'])

                for idx, image in enumerate(images):
                    SaveImg(image, path = title_path+f'/sentence_{idx}.png')

            
            except:
                print("\nGetImg로 이미지를 생성합니다.\n")
                for idx in range(3):
                    image = ImgGenerator(summary[f'Prompt{idx}'])
                    SaveImg(image, path = title_path+f'/sentence_{idx}.png')
            
            
            # title,summary, keywords,tts, images= Generate.SeperateSentence(content)
            # json_path = SaveSeperateData(path, crawl, title, summary,keywords,tts, images)

            # data.json 파일 읽기
            with open(json_path, 'r', encoding='UTF-8') as json_file:
                data_content = json.load(json_file)

            # title을 data_content에서 추출
            title = data_content['title']
            print("data" + title)

            # 비디오 생성 및 저장
            print(crawl['section'])
            video_path = f"{path}/final_output.mp4"
            Video.generate_video(crawl['section'], title)  

            # with 광고 비디오 생성 및 저장
            Video.addAdVideo()
            video_withad_path = f"{path}/final_output_withad.mp4"
            
            # 숏폼 S3에 업로드
            url = save_to_s3(video_path, SHORTFORM_BUCKET_NAME, f"{id_list[id_idx]}.mp4")

            # with 광고 숏폼 S3 업로드
            save_to_s3(video_withad_path, WITHAD_BUCKET_NAME, f"{id_list[id_idx]}.mp4")
            
            # 썸네일 S3에 업로드
            thumbnail_path = f"{path}/sentence_0.png"
            adjusted_thumbnail_path = f"{path}/adjusted_sentence_0.png"
            adjust_thumbnail_to_9_16(thumbnail_path, adjusted_thumbnail_path)

            thumbnail_url = save_to_s3(adjusted_thumbnail_path, THUMBNAIL_BUCKET_NAME, f"{id_list[id_idx]}.png")
            print(f"thumbnail_url : {thumbnail_url}")

            # S3내 객체 이름이 될 id 인덱스 증가
            id_idx += 1

            # 반환값
            response.append(ComponentResponse(data=data_content, s3=url, thumbnail=thumbnail_url))
    
    return response


if __name__ == '__main__':
    # MakeComponent(10,10,10)
    # 파라미터 주요뉴스 갯수, 스포츠 뉴스, 연예 뉴스 갯수
    MakeSeperateComponent(1, 0, 0)