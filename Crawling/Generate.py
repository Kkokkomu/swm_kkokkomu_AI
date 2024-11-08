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

characters_dic ={'woman1':'Emma','woman2':'Olivia','woman3':'Sophia','woman4':'Ava','man1':'Liam','man2':'Ethan','man3':'Noah','man4':'James'}


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

    system = '''다음 뉴스를 제목을 한국어로 15자 이내로 지어 주고 제목만 읽어도 무슨 내용인지 대충 유추할 수 있고, 강렬한 인상을 줄 수 있게 작성해줘, 내용을 정확히 3문장으로 요약해주고 각 문장을 자연스럽게 이어줘. 필요한 경우 요약문의 각 문장 사이를 접속사를 이용해서 자연스럽게 연결해줘. 요약할때 말투는 무조건 ~했습니다 와 같은 말투로 해. 
    그리고 요약된 3문장 각각에 해당되는 이미지를 구체적으로 묘사하고 prompt로 말해. 묘사할때 obsession with impressions, where, what, atmosphere, subject, color, lighting, extra details 의 주제에 맞게 최대한 상세하게 영어로 표현해. 특히 장소에 대한 묘사를 최대한 세부적으로 표현해. 예를 들어 stadium이면 baseball stadium인지 football stadium인지 정확하게 말해줘.
    답변을 json형식으로 말해. 예시로는 {"title" : "제목", "summary" : "요약문", 
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
    return find_json(response)

def generate_keywords(text):
    gpt_version = 'gpt-4o-mini'

    system = '''다음 뉴스를 읽고 키워드 3개를 추출해. 답변을 json형식으로 말해. 예시로는 {"keyword" : "keyword1, keyword2, keyword3"}으로 말해'''

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
    return find_json(response)


def TransPronounce(text):
    gpt_version = 'gpt-4o-mini'

    system = '''다음 문장에 적힌 내용의 영어를 한국어로 표기해. 결과는 json형식으로 표현해. 
                예를 들어 samsung은 삼성, SK는 에스케이, LG는 엘지, U+는 유플러스로 작성해줘. 결과 예시는 
                KT 위즈의 문상철이 준플레이오프 1차전에서 LG 트윈스를 상대로 선제 투런 홈런을 기록했습니다. 문상철은 2회초 첫 타석에서 LG 선발 투수를 상대로 강력한 타격을 선보이며 팀의 리드를 가져왔습니다. 이강철 감독의 타순 변경 결정이 성공적으로 작용하며 문상철은 기대에 부응하는 활약을 보여주었습니다. 라는 문장을 받으면
                {"Pronounce" : "케이티 위즈의 문상철이 준플레이오프 1차전에서 엘지 트윈스를 상대로 선제 투런 홈런을 기록했습니다. 문상철은 2회초 첫 타석에서 엘지 선발 투수를 상대로 강력한 타격을 선보이며 팀의 리드를 가져왔습니다. 이강철 감독의 타순 변경 결정이 성공적으로 작용하며 문상철은 기대에 부응하는 활약을 보여주었습니다."}의 결과가 나오게 해줘'''
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

    return find_json(response)


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
    

    try:
        response = json.loads(response)
        response_prompts = {f'Prompt{i}' :response[f'Prompt{i}'] for i in range(3)}

        title = response['title']
        summary_total = response['summary']
        
        summarys = re.sub(r'다\. ','다.\n',summary_total)
        summarys = summarys.split('\n')


        pronounce_summary = TransPronounce(summary_total)
        pronounce_summary=json.loads(pronounce_summary)
        pronounce_summary = pronounce_summary['Pronounce']

        pronounce_summarys = re.sub(r'다\. ','다.\n',pronounce_summary)
        pronounce_summarys = pronounce_summarys.split('\n')

        print(pronounce_summarys)


        character_response = FindCharacters(summary_total)

        character_response = find_json(character_response)
        character_response = json.loads(character_response)

        character_set = character_response[f'sentence_Character0']
        
        characters ={}

        if len(summarys) != 3:
            raise

        summary_dic = {f'sentence_{i}' : summary for i,summary in enumerate(summarys)}
        for i, ps in enumerate(pronounce_summarys):
            summary_dic[f'Pronounce_{i}']= ps

            

        summary_dic['Pronounce_total']= pronounce_summary
        
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
        keywords = generate_keywords(text)
        keywords = json.loads(keywords)
        keywords = keywords['keyword']
        
    except Exception as e:    # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
        print('예외가 발생했습니다.', e)
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

    return find_json(response)

def TransPronounce(text):
    gpt_version = 'gpt-4o-mini'

    system = '''다음 문장에 적힌 내용의 영어를 한국어로 표기해. 결과는 json형식으로 표현해. 
                예를 들어 samsung은 삼성, SK는 에스케이, LG는 엘지, U+는 유플러스로 작성해줘. 결과 예시는 
                KT 위즈의 문상철이 준플레이오프 1차전에서 LG 트윈스를 상대로 선제 투런 홈런을 기록했습니다. 문상철은 2회초 첫 타석에서 LG 선발 투수를 상대로 강력한 타격을 선보이며 팀의 리드를 가져왔습니다. 이강철 감독의 타순 변경 결정이 성공적으로 작용하며 문상철은 기대에 부응하는 활약을 보여주었습니다. 라는 문장을 받으면
                {"Pronounce" : "케이티 위즈의 문상철이 준플레이오프 1차전에서 엘지 트윈스를 상대로 선제 투런 홈런을 기록했습니다. 문상철은 2회초 첫 타석에서 엘지 선발 투수를 상대로 강력한 타격을 선보이며 팀의 리드를 가져왔습니다. 이강철 감독의 타순 변경 결정이 성공적으로 작용하며 문상철은 기대에 부응하는 활약을 보여주었습니다."}의 결과가 나오게 해줘'''
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

    return find_json(response)


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

    return find_json(response)

if __name__ == '__main__':
    text = """국민의힘 윤상현 의원은 10일 한동훈 대표를 겨냥해 "김 여사에 대한 악마화 작업에 부화뇌동하는 것이 아니라면 자해적 발언을 삼가야 한다"고 비판했다.
윤 의원은 이날 한 대표가 김건희 여사의 도이치모터스 주가조작 연루 의혹에 대한 검찰 기소 판단과 관련해 "국민이 납득할만한 결과를 내놔야 한다"고 주문한 것을 두고 이같이 말했다.
그는 소셜미디어(SNS)에 글을 올려 "수사가 객관적 사실과 법리에 근거해서 결론 내는 거지 국민 눈높이에 맞추라는 식은 법무부 장관까지 했던 사람의 발언으로는 상상조차 하기 어렵다"고 지적했다.
이어 "법과 원칙에 맞는 수사대신 여론재판을 열자는 것인가"라며 "지금은 법리와 증거에 기반한 수사에 따라 진실이 밝혀지길 기다릴 때"라고 강조했다.
앞서 한 대표는 이날 '검찰이 도이치모터스 사건에 대해 김 여사를 불기소할 것 같다'는 취재진 질문에 "검찰이 어떤 계획을 가지고 있는지 알지 못한다"면서도 "검찰이 국민이 납득할만한 결과를 내놔야 한다"고 밝혔다.
그는 김 여사의 활동 자제가 필요하다고 했던 자신의 입장과 관련해서는 "당초 대선에서 국민에게 약속한 부분 아닌가. 그것을 지키면 된다"고 말했다."""
    # text = """미국 뉴욕증시가 최근 강세를 보이고 있는 가운데, 이 같은 상황이 미국 민주당 카멀라 해리스 대선 후보의 승리 가능성을 암시한다는 분석이 나왔다.
    

# 지난달 31일(현지시각) 폴리티코에 따르면, 금융서비스 기업 LPL 파이낸셜은 스탠더드앤드푸어스(S&P)500지수 성과가 '백악관 주인'에 대한 단서를 보여준다는 분석을 내놨다.

# 대선 투표일 직전 3개월 동안 이 지수가 오르면 현 집권당 대선 후보가 승리하고, 지수가 하락하면 반대 결과가 나오는 경향이 있다는 주장이다.

# S&P500 지수는 글로벌 신용평가사 스탠더드앤드푸어스가 우량주를 중심으로 선정한 500개 기업의 주가지수로, 시장 투자자들의 심리가 반영돼 움직인다.

# 즉 해당 지수가 오른다는 것은 투자자들이 현 집권당의 임기 연장을 통해 불확실성을 제거하길 원한다는 뜻으로 해석될 수 있다는 것이다.
# 반대로 이 지수가 떨어지는 경우 투자자들이 새로운 행정부를 원하며 그에 따른 불확실성에 대비하고 있다는 뜻으로 풀이될 수 있다는 것이다.

# 이 기업의 주장대로라면, 이번 대선에서 해리스 후보가 승리할 가능성이 더 높다. 대선 3개월 전인 지난 8월 이후부터 현재까지 S&P500 지수는 10%가량 상승했기 때문이다.

# LPL 파이낸셜은 1924년 대선 이후부터 2020년 대선까지 96년 동안 단 4번을 제외하고 이 같은 경향이 들어맞았다는 점을 근거로 들었다.

# LPL 파이낸셜 수석 기술 전략가인 애덤 턴키스트는 "현 집권당이 백악관을 차지할 것이라는 확신이 더 커질 때, S&P500 지수는 오른다"며 "현 집권당의 정책 흐름이 향후에도 이어져, 시장이 안도감을 느끼는 것"이라고 말했다.

# 그러면서 "우리가 수집한 데이터에 따르면, 시장은 해리스 후보가 이길 것으로 예측하고 있다"고 전했다.

# 다만 폴리티코는 이 같은 주장에 대해 "S&P500 지수는 완벽한 예측 도구가 아니다"며 2020년 대선을 거론했다.

# 당시 S&P500 지수는 오름세를 거듭하며 공화당 도널드 트럼프 당시 대통령이 재선에 성공할 가능성을 보여줬으나, 실제로는 조 바이든 당시 민주당 후보에게 패배했다.

# 모건스탠리 웰스 매니지먼트의 미국 정책 책임자인 모니카 게라는 폴리티코에 "시장은 (결과를 미리 보여주는) 수정 구슬이 아니다"고 말했다.

# 그는 S&P500의 상승세는 소수의 빅테크 기업이나 연방준비제도(Fed·연준)의 금리 정책이 견인했다고 덧붙였다.

# 트럼프 후보의 승리를 점치는 증거들도 넘쳐난다는 의견도 나왔다.

# 모건스탠리는 최근 연구보고서를 내어 각 당의 승리로 수혜를 볼 수 있는 투자 상품 '바스켓'을 분석한 결과, 지난 한 해 동안 공화당 바스켓이 민주당 바스켓보다 10%가량 높았다고 밝혔다.

# 미국의 전설적인 투자자인 스탠리 드러켄밀러는 최근 블룸버그TV에서 "시장 내부에서는 트럼프 후보가 이길 것이라고 확신하고 있다"며 은행 주식, 암호화폐 가격, 트럼프 미디어 주가 급등 등을 근거로 들었다.

# 한편 이날 기준 뉴욕타임스(NYT) 평균에 따르면 해리스 후보(49%)와 트럼프 후보(48%)는 1%p 차이로 역대 어느 대선보다 박빙의 승부를 보이고 있다.

# 선거 예측 모델 파이브서티에이트(538) 평균에서도 현재 기준 해리스 후보가 47.9%대 46.7%로 1.2%p 앞서고 있다. 오차범위 내 차이다.

# 정치전문매체 더힐과 디시전데스크HQ의 317개 여론조사 평균에선 해리스 후보가 48.1%로 트럼프 후보(47.7%)를 소폭 앞서고 있다. 트럼프 후보가 당선될 확률은 53%로 보고 있다.
# """
    response = generation_summary(text)
    print(response)
