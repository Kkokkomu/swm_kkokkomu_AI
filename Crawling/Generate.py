from openai import OpenAI
import json
import re
from ImgGenerator import ImgGenerator

import os
import sys
import urllib.request
import urllib.parse

with open('./secret.json') as f:
    secrets = json.loads(f.read())
    
SECRET_KEY = secrets['API_Key']

CLOVA_CLIENT_ID = secrets['CLOVA_CLIENT_ID']
CLOVA_CLIENT_SECRET = secrets['CLOVA_CLIENT_SECRET']

client = OpenAI(
    api_key=SECRET_KEY,
)


def find_json(text):

    pattern = re.compile(r'\{(.*?)\}', re.DOTALL)
    match = pattern.search(text)
    # print(match.group(0))
    return match.group(0)


def generation_summary(text):
    # gpt_version ='gpt-3.5-turbo-0125'
    gpt_version = 'gpt-4o-mini'

    system = '다음 뉴스를 제목지어 주고 내용을 정확히 3문장으로 이야기하듯이 요약하고 주요한 키워드 3개 뽑아. 요약할때 말투는 무조건 ~했습니다 와 같은 말투로 해. 답변을 json형식으로 말해. 예시로는 {"title" : "제목", "summary" : "요약문", "keyword" : "keyword1, keyword2, keyword3"}으로 말해'

    response_sum = client.chat.completions.create(
        model=gpt_version,  # 또는 다른 모델을 사용
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ],
    )


    response = response_sum.json()
    response = json.loads(response)
    response = response["choices"][0]["message"]['content']
    return response


def generate_TTS(text):
    response_tts = client.audio.speech.create(
        model="tts-1-hd",
        speed=1,
        voice="nova",
        input=text,
    )
    return response_tts

def generate_TTS_clova(text):
    client_id = CLOVA_CLIENT_ID  # Clova API Client ID
    client_secret = CLOVA_CLIENT_SECRET  # Clova API Client Secret
    text = str(text)  # Python 3에서 unicode는 str로 대체됨
    speaker = "ngoeun"
    speed = "1"
    volume = "1"
    pitch = "1"
    fmt = "wav"
    val = {
        "speaker": speaker,
        "volume": volume,
        "speed": speed,
        "pitch": pitch,
        "text": text,
        "format": fmt,
        "sampling-rate": 24000
    }

    # 요청 데이터 확인 로그
    print("TTS 요청 데이터:", val)

    data = urllib.parse.urlencode(val).encode("utf-8")  # data를 인코딩
    url = "https://naveropenapi.apigw.ntruss.com/tts-premium/v1/tts"
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret
    }

    # 요청 URL 및 헤더 로그
    print("TTS 요청 URL:", url)
    print("TTS 요청 헤더:", headers)

    request = urllib.request.Request(url, data, headers)

    print('TTS API 요청 시작...')
    try:
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        print(f'TTS 응답 코드: {rescode}')
        
        if rescode == 200:
            print("TTS wav 생성 성공")
            return response.read()
        else:
            print("TTS 요청 실패, 응답 코드:", rescode)
    except Exception as e:
        print("TTS API 요청 중 예외 발생:", str(e))

def generate_total(text):
    response = generation_summary(text)
    try:
        response = find_json(response)
        response = json.loads(response)

        title = response['title']
        summary = response['summary']

        tts = generate_TTS(summary)
    except:
        title, summary, tts = generate_total(text)

    return title, summary, tts


def SeperateSentence(text):
    print('generate summary')
    response = generation_summary(text)
    response = find_json(response)

    try:
        response = json.loads(response)

        title = response['title']
        print(title)
        summary_total = response['summary']
        print(summary_total)
        summarys = re.sub(r'다\. ','다.\n',summary_total)
        summarys = summarys.split('\n')

        if len(summarys) != 3:
            raise
        summary_dic = {f'sentence_{i}' : summary for i,summary in enumerate(summarys)}
        
        response_prompts = TransSummary(summary_total)
        response_prompts = find_json(response_prompts)
        response_prompts = json.loads(response_prompts)


        if len(response_prompts) != 3:
            raise

        summary_dic.update(response_prompts)
        summary_dic['sentence_total'] = summary_total
        keywords = response['keyword']

        print('generate tts')
        tts = [generate_TTS_clova(summary) for summary in summarys]

        print('generate image')
        images = []
        for idx in range(3):
            response_img = ImgGenerator(summary_dic[f'Prompt{idx}'])
            images.append(response_img)
    except:

        title, summary_dic,keywords ,tts, images = SeperateSentence(text)
    return title, summary_dic, keywords ,tts, images



def TransSummary(text):
    gpt_version = 'gpt-4o-mini'

    system = '다음 3문장을 각각 상황에 맞게 묘사해. 묘사할때 subject, color, lighting, extra details 의 주제에 맞게 영어로 표현해. 특정 인물 이름 빼! 남자는 boy 나 man 여자는 girl 이나 woman으로 표시해! 예시로는 json 형식으로  {"Prompt0": "A corgi dog sitting on the front porch, brown, studio lighting, utopian future", "Prompt1": "A cat standing on the front porch, brown, studio lighting, utopian future", "Prompt2": "A man open the door, brown, studio lighting, utopian future"}'

    response_sum = client.chat.completions.create(
        model=gpt_version,  # 또는 다른 모델을 사용
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ],
    )

    response = response_sum.json()
    response = json.loads(response)
    response = response["choices"][0]["message"]['content']
    response = response.split('Prompt:')[-1].strip()

    return response

if __name__ == '__main__':
    text = "박태준은 2024 파리 올림픽 태권도 남자 58kg급 준결승에서 세계랭킹 1위의 모하메드 칼릴 젠두비를 2-0으로 제압하며 결승에 진출했습니다. 공격적인 플레이로 연속 점수를 올린 박태준은 기량을 뽐내며 관중의 환호를 받았습니다. 8일 결승에서 박태준은 태권도 금메달에 도전하게 됩니다."
    response = TransSummary(text)
    print(response)
