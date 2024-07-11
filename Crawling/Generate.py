from openai import OpenAI
import json
import re
from ImgGenerator import ImgGenerator
from Generalize import Generalize

with open('./secret.json') as f:
    secrets = json.loads(f.read())
    
SECRET_KEY = secrets['API_Key']

client = OpenAI(
    api_key=SECRET_KEY,
)


def generation_summary(text):
    
    gpt_version ='gpt-3.5-turbo-0125'

    system = '다음 뉴스를 제목지어 주고 내용을 정확히 3문장으로 이야기하듯이 요약해줘. 요약할때 말투는 무조건 ~했습니다 와 같은 말투로 해. 결과물은 json 형식으로 {title : 제목, summary : 요약문}과 같은 형식으로 전달해줘'

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


def generate_total(text):
    response = generation_summary(text)
    try:
        response = json.loads(response)

        title = response['title']
        summary = response['summary']

        tts = generate_TTS(summary)
    except:
        title, summary, tts = generate_total(text)

    return title, summary, tts



def SeperateSentence(text):
    response = generation_summary(text)

    try:
        response = json.loads(response)

        title = response['title']
        summary_total = response['summary']
        summarys = re.sub(r'다\. ','다.\n',summary_total )
        summarys = summarys.split('\n')
        if len(summarys) != 3:
            raise
        summary_dic = {f'sentence_{i}' : summary for i,summary in enumerate(summarys)}
        for i, summary in enumerate(summarys):
            # summary_dic[f'trans_sentence{i}'] = TransSummary(summary)
            summary_dic[f'trans_sentence{i}'] = TransSummary(Generalize(summary))
        summary_dic['sentence_total'] = summary_total
        summary_dic['trans_sentence'] = TransSummary(summary_total)

        tts = [generate_TTS(summary) for summary in summarys]
        images = []
        for idx in range(3):
            response = ImgGenerator(summary_dic[f'trans_sentence{idx}'])
            images.append(response)
    except:
        # title, summary_dic, tts = SeperateSentence(text)
        title, summary_dic, tts, images = SeperateSentence(text)
        
    return title, summary_dic, tts, images


def TransSummary(text):
    gpt_version ='gpt-3.5-turbo-0125'

    system = '영어로 번역해줘'

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





