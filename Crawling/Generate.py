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

# CLOVA_CLIENT_ID = secrets['CLOVA_CLIENT_ID']
# CLOVA_CLIENT_SECRET = secrets['CLOVA_CLIENT_SECRET']

client = OpenAI(
    api_key=SECRET_KEY,
)

characters_dic ={'woman1':'Olivia','woman2':'Emma','woman3':'Sophia','woman4':'Ava','man1':'Ethan','man2':'Liam','man3':'Noah','man4':'James'}


def sanitize_filename(filename):
    
    # 사용할 수 없는 문자 목록: \ / : * ? " < > |
    unsafe_characters = r'[:*?"<>|]'
    # 사용할 수 없는 문자를 '_'로 대체
    return re.sub(unsafe_characters, '_', filename)


def find_json(text):

    pattern = re.compile(r'\{(.*?)\}', re.DOTALL)
    match = pattern.search(text)
    # print(match.group(0))
    return match.group(0)


def generation_summary(text):
    # gpt_version ='gpt-3.5-turbo-0125'
    gpt_version = 'gpt-4o-mini'

    system = '''다음 뉴스를 제목지어 주고 내용을 정확히 3문장으로 이야기하듯이 요약하고 주요한 키워드 3개 뽑아. 요약할때 말투는 무조건 ~했습니다 와 같은 말투로 해. 
    그리고 요약된 3문장 각각에 해당되는 이미지를 구체적으로 묘사하고 prompt로 말해. 묘사할때 obsession with impressions, where, what, atmosphere, subject, color, lighting, extra details 의 주제에 맞게 최대한 상세하게 영어로 표현해. 특히 장소에 대한 묘사를 최대한 세부적으로 표현해. 예를 들어 stadium이면 baseball stadium인지 football stadium인지 정확하게 말해줘.
    답변을 json형식으로 말해. 예시로는 {"title" : "제목", "summary" : "요약문", "keyword" : "keyword1, keyword2, keyword3", "sentence_Character0": "man1", "sentence_Character1": "man1 woman1", "sentence_Character2": "woman1",
    "Prompt0": "wear suit, National Assembly​​,presenting in front of people, glad , stand in front of people, brown, studio lighting, utopian future", 
    "Prompt1": "casual clothes, dimly lit room, focused on screen, concentrate ,cluttered with books and gadgets, blue glow from monitor, obsessed with learning", 
    "Prompt2": "red dress, open field, comfort ,midday sun, green grass, carefree expression, short sharp shadows, pure joy"}으로 말해'''

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
    speed = "-1"
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

def makeJson(text):
    response = generation_summary(text)
    response = find_json(response)

    try:
        response = json.loads(response)
        response_prompts = {f'Prompt{i}' :response[f'Prompt{i}'] for i in range(3)}

        title = response['title']
        summary_total = response['summary']
        summarys = re.sub(r'다\. ','다.\n',summary_total)
        summarys = summarys.split('\n')

        character_response = FindCharacters(summary_total)

        character_response = find_json(character_response)
        character_response = json.loads(character_response)

        character_set = character_response[f'sentence_Character0']
        
        characters ={}



        if len(summarys) != 3:
            raise

        summary_dic = {f'sentence_{i}' : summary for i,summary in enumerate(summarys)}
        
        prompt_total = ""
        for i in range(3):
            character_set = character_response[f'sentence_Character{i}']

            prompt = response[f'Prompt{i}']

            if character_set =='none':
                prompt = prompt.split(',')[1:]
                prompt = ','.join(prompt)
            else: 
                character_list = character_set.strip().split(' ')
                for character in character_list:
                    if character == 'none':
                        
                        continue
                    prompt_total += characters_dic[character] + ', '
            characters[f'sentence_{i}'] = character_set
            prompt_total += prompt

            if not i ==2:
                prompt_total += ' \n '

        summary_dic['prompt_total'] = prompt_total
        
        summary_dic.update(response_prompts)


        summary_dic['sentence_total'] = summary_total
        keywords = response['keyword']
        
    except:
        title, summary_dic, keywords, characters = makeJson(text)
        
    
    return title, summary_dic, keywords, characters


def FindCharacters(text):

    gpt_version = 'gpt-4o-mini'

    system = '''다음 3문장에 해당되는 인물의 성별을 적어줘. 만약 사람이 여러명 나오면 man1, man2, woman1, woman2 와 같이 표현하고 없으면 none으로 표시해. 그리고 윤석열이랑 윤대통령과 같이 직책앞에 성을 붙이는 건 성이 같으면 같은사람이야. '그' 나 '그녀'와 같이 대명사를 쓰는 것도 포함시켜. 결과는 Json 형식으로 추출해.
    예를 들어 '이승기는 정대세를 매력적인 '하극상' 캐릭터로 설명했습니다. 그는 정대세가 사회적 불편함을 다양한 매력으로 전환하는 인물이라고 밝혔습니다. '생존왕'은 10월 7일 첫 방송되며 총 12명의 멤버가 생존 대결을 펼칠 예정입니다.' 라는 요약이면 
    {"sentence_Character0": "man1 man2", "sentence_Character1": "man1 man2", "sentence_Character2": "none"}으로 대답해. 
    '''

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
 



def TransSummary(text):
    gpt_version = 'gpt-4o-mini'

    system = '''다음 3문장을 각각 상황에 맞게 묘사해. 묘사할때 obsession with impressions, where, what, atmosphere, subject, color, lighting, extra details 의 주제에 맞게 최대한 상세하게 영어로 표현해. 특히 장소에 대한 묘사를 최대한 세부적으로 표현해. 예를 들어 stadium이면 baseball stadium인지 football stadium인지 정확하게 말해줘.
    전체 예시로는 json 형식으로  {"Prompt0": "wear suit, National Assembly​​,presenting in front of people, glad , stand in front of people, brown, studio lighting, utopian future", 
    "Prompt1": "casual clothes, dimly lit room, focused on screen, concentrate ,cluttered with books and gadgets, blue glow from monitor, obsessed with learning", 
    "Prompt2": "red dress, open field, comfort ,midday sun, green grass, carefree expression, short sharp shadows, pure joy"}'''

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
    text = """국민의힘 윤상현 의원은 10일 한동훈 대표를 겨냥해 "김 여사에 대한 악마화 작업에 부화뇌동하는 것이 아니라면 자해적 발언을 삼가야 한다"고 비판했다.
윤 의원은 이날 한 대표가 김건희 여사의 도이치모터스 주가조작 연루 의혹에 대한 검찰 기소 판단과 관련해 "국민이 납득할만한 결과를 내놔야 한다"고 주문한 것을 두고 이같이 말했다.
그는 소셜미디어(SNS)에 글을 올려 "수사가 객관적 사실과 법리에 근거해서 결론 내는 거지 국민 눈높이에 맞추라는 식은 법무부 장관까지 했던 사람의 발언으로는 상상조차 하기 어렵다"고 지적했다.
이어 "법과 원칙에 맞는 수사대신 여론재판을 열자는 것인가"라며 "지금은 법리와 증거에 기반한 수사에 따라 진실이 밝혀지길 기다릴 때"라고 강조했다.
앞서 한 대표는 이날 '검찰이 도이치모터스 사건에 대해 김 여사를 불기소할 것 같다'는 취재진 질문에 "검찰이 어떤 계획을 가지고 있는지 알지 못한다"면서도 "검찰이 국민이 납득할만한 결과를 내놔야 한다"고 밝혔다.
그는 김 여사의 활동 자제가 필요하다고 했던 자신의 입장과 관련해서는 "당초 대선에서 국민에게 약속한 부분 아닌가. 그것을 지키면 된다"고 말했다."""
    response = makeJson(text)
    print()
    print(response)
