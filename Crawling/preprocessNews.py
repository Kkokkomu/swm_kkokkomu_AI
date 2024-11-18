import re
# from konlpy.tag import Kkma
from collections import OrderedDict

# HTML 태그를 제거
def remove_html(texts):
    """
    HTML 태그를 제거합니다.
    ``<p>안녕하세요 ㅎㅎ </p>`` -> ``안녕하세요 ㅎㅎ ``
    """
    preprcessed_text = []
    for text in texts:

        text = re.sub(r"<[^>]+>\s+(?=<)|<[^>]+>", "", text).strip()
        if text:
            preprcessed_text.append(text)

    return preprcessed_text

# 이메일 제거 
def remove_email(texts):
    preprocess_text = []
    for text in texts:
        text = re.sub(r"[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "", text).strip()
        if text:
            preprocess_text.append(text)
    return preprocess_text


# 언론정보 제거
def remove_press(texts):
    """
    언론 정보를 제거합니다.
    ``홍길동 기자 (연합뉴스)`` -> ````
    ``(이스탄불=연합뉴스) 하채림 특파원 -> ````
    """
    re_patterns = [
        r"\([^(]*?(뉴스|경제|일보|미디어|데일리|한겨례|타임즈|위키트리)\)",
        r"[가-힣]{1,4} (기자|선임기자|수습기자|특파원|객원기자|논설고문|통신원|연구소장)",  # 이름 + 기자
        r"[가-힣]{1,4}(기자|선임기자|수습기자|특파원|객원기자|논설고문|통신원|연구소장)",  # 이름 + 기자
        r"[가-힣]{1,}(뉴스|경제|일보|미디어|데일리|한겨례|타임|위키트리)",  # (... 연합뉴스) ..
        r"\(\s+\)",  # (  )
        r"\(=\s+\)",  # (=  )
        r"\(\s+=\)",  # (  =)
    ]

    preprocessed_text = []
    for text in texts:
        for re_pattern in re_patterns:
            text = re.sub(re_pattern, "", text).strip()
        if text:
            preprocessed_text.append(text)
    return preprocessed_text


def remove_copyright(texts):
    """
    뉴스 내 포함된 저작권 관련 텍스트를 제거합니다.
    ``(사진=저작권자(c) 연합뉴스, 무단 전재-재배포 금지)`` -> ``(사진= 연합뉴스, 무단 전재-재배포 금지)`` TODO 수정할 것
    """
    re_patterns = [
        r"\<저작권자(\(c\)|ⓒ|©|\(Copyright\)|(\(c\))|(\(C\))).+?\>",
        r"저작권자\(c\)|ⓒ|©|(Copyright)|(\(c\))|(\(C\))"
    ]
    preprocessed_text = []
    for text in texts:
        for re_pattern in re_patterns:
            text = re.sub(re_pattern, "", text).strip()
        if text:
            preprocessed_text.append(text)
    return preprocessed_text


def remove_photo_info(texts):
    """
    뉴스 내 포함된 이미지에 대한 label을 제거합니다.
    ``(사진= 연합뉴스, 무단 전재-재배포 금지)`` -> ````
    ``(출처=청주시)`` -> ````
    """
    preprocessed_text = []
    for text in texts:
        text = re.sub(r"\(출처?=?.+\)|\(출처 ?= ?.+\) |\[[^=]+=[^\]]+\)|\([^=]+=[^\)]+\)|\(사진 ?= ?.+\) |\(자료 ?= ?.+\)| \(자료사진\) |사진=.+기자 ", "", text).strip()
        if text:
            preprocessed_text.append(text)
    return preprocessed_text


# 첫번째에 = 이 오는경우
def removefirst(texts):
    if not texts:
        pass
    elif texts[0][0] == '=':
        texts[0] = texts[0][1:].strip()
    return texts



def remove_useless_breacket(texts):
    """
    위키피디아 전처리를 위한 함수입니다.
    괄호 내부에 의미가 없는 정보를 제거합니다.
    아무런 정보를 포함하고 있지 않다면, 괄호를 통채로 제거합니다.
    ``수학(,)`` -> ``수학``
    ``수학(數學,) -> ``수학(數學)``
    """
    bracket_pattern = re.compile(r"\((.*?)\)")
    preprocessed_text = []
    for text in texts:
        modi_text = ""
        text = text.replace("()", "")  # 수학() -> 수학
        brackets = bracket_pattern.search(text)
        if not brackets:
            if text:
                preprocessed_text.append(text)
                continue
        replace_brackets = {}
        # key: 원본 문장에서 고쳐야하는 index, value: 고쳐져야 하는 값
        # e.g. {'2,8': '(數學)','34,37': ''}
        while brackets:
            index_key = str(brackets.start()) + "," + str(brackets.end())
            bracket = text[brackets.start() + 1 : brackets.end() - 1]
            infos = bracket.split(",")
            modi_infos = []
            for info in infos:
                info = info.strip()
                if len(info) > 0:
                    modi_infos.append(info)
            if len(modi_infos) > 0:
                replace_brackets[index_key] = "(" + ", ".join(modi_infos) + ")"
            else:
                replace_brackets[index_key] = ""
            brackets = bracket_pattern.search(text, brackets.start() + 1)
        end_index = 0
        for index_key in replace_brackets.keys():
            start_index = int(index_key.split(",")[0])
            modi_text += text[end_index:start_index]
            modi_text += replace_brackets[index_key]
            end_index = int(index_key.split(",")[1])
        modi_text += text[end_index:]
        modi_text = modi_text.strip()
        if modi_text:
            preprocessed_text.append(modi_text)
    return preprocessed_text

def remove_dup_sent(texts):
    """
    중복된 문장을 제거합니다.
    """
    texts = list(OrderedDict.fromkeys(texts))
    return texts

## 다.로 끝나지 않는 문장 제거
def not_sentence(texts):
    preproccessed_text = []
    for text in texts:
        if text[-2:] == "다.":
            preproccessed_text.append(text)
    return preproccessed_text


# def morph_filter(texts):
#     """
#     명사(NN), 동사(V), 형용사(J)의 포함 여부에 따라 문장 필터링
#     """
#     NN_TAGS = ["NNG", "NNP", "NNB", "NP"]
#     V_TAGS = ["VV", "VA", "VX", "VCP", "VCN", "XSN", "XSA", "XSV"]
#     J_TAGS = ["JKS", "J", "JO", "JK", "JKC", "JKG", "JKB", "JKV", "JKQ", "JX", "JC", "JKI", "JKO", "JKM", "ETM"]
#     tagger = Kkma()

#     preprocessed_text = []
#     for text in texts:
#         morphs = tagger.pos(text, join=False)

#         nn_flag = False
#         v_flag = False
#         j_flag = False
#         for morph in morphs:
#             pos_tags = morph[1].split("+")
#             for pos_tag in pos_tags:
#                 if not nn_flag and pos_tag in NN_TAGS:
#                     nn_flag = True
#                 if not v_flag and pos_tag in V_TAGS:
#                     v_flag = True
#                 if not j_flag and pos_tag in J_TAGS:
#                     j_flag = True
#             if nn_flag and v_flag and j_flag:
#                 preprocessed_text.append(text)
#                 break
#     return preprocessed_text
def removeBracket(texts):
    preprocessed_text = []

    for text in texts:
        text = re.sub(r'\[.*?\]', '', text)
        if text:
            preprocessed_text.append(text.strip())
    return preprocessed_text


def replace_da_period(text):
    # 따옴표 안의 내용을 찾는 정규표현식
    quoted_pattern = r'(".*?"|\'.*?\')'
    # 따옴표 안의 내용을 제외한 나머지 부분을 찾는 정규표현식
    non_quoted_pattern = r'([^"\']+|(?<=\w)["\'][^"\']*["\'])'
    
    # 따옴표 안의 내용을 리스트로 저장
    quoted_parts = re.findall(quoted_pattern, text)
    
    # 따옴표 안의 내용을 플레이스홀더로 대체
    temp_text = re.sub(quoted_pattern, '{}', text)
    
    # 따옴표 안의 내용을 제외한 부분에서 '다.'를 '다.\n'로 변경
    replaced_text = re.sub(r'다\.', '다.\n', temp_text)
    
    # 플레이스홀더를 원래의 따옴표 안의 내용으로 대체
    final_text = replaced_text.format(*quoted_parts)
    
    return final_text


def removeAll(texts):

    texts = remove_dup_sent(texts)
    texts = remove_html(texts)
    texts = remove_email(texts)
    texts = remove_press(texts)
    texts = remove_copyright(texts)
    texts = remove_photo_info(texts)
    texts = remove_useless_breacket(texts)
    texts = not_sentence(texts)
    texts = removeBracket(texts)
    texts = remove_dup_sent(texts)
    texts = removefirst(texts)

    return texts

 #언론정보 제거
def remove_press_one(text):
    """
    언론 정보를 제거합니다.
    ``홍길동 기자 (연합뉴스)`` -> ````
    ``(이스탄불=연합뉴스) 하채림 특파원 -> ````
    """
    re_patterns = [
        r"\([^(]*?(뉴스|경제|일보|미디어|데일리|한겨례|타임즈|위키트리)\)",
        r"[가-힣]{1,4} (기자|선임기자|수습기자|특파원|객원기자|논설고문|통신원|연구소장)",  # 이름 + 기자
        r"[가-힣]{1,4}(기자|선임기자|수습기자|특파원|객원기자|논설고문|통신원|연구소장)",  # 이름 + 기자
        r"[가-힣]{1,}(뉴스|경제|일보|미디어|데일리|한겨례|타임|위키트리)",  # (... 연합뉴스) ..
        r"\(\s+\)",  # (  )
        r"\(=\s+\)",  # (=  )
        r"\(\s+=\)",  # (  =)
    ]


    for re_pattern in re_patterns:
        text = re.sub(re_pattern, "", text).strip()
    return text



def replace_html_entities(text):
    replacements = {
        "&nbsp;": " ",
        "&lt;": "<",
        "&gt;": ">",
        "&amp;": "&",
        "&quot;": "\"",
        "&#035;": "#",
        "&#039;": "'"
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def remove_email_one(text):
    text = re.sub(r"[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "", text).strip()
    return text

def remove_html_one(text):
    """
    HTML 태그를 제거합니다.
    ``<p>안녕하세요 ㅎㅎ </p>`` -> ``안녕하세요 ㅎㅎ ``
    """

    text = re.sub(r"<[^>]+>\s+(?=<)|<[^>]+>", "", text).strip()

    return text

def remove_photo_info_one(text):
    """
    뉴스 내 포함된 이미지에 대한 label을 제거합니다.
    ``(사진= 연합뉴스, 무단 전재-재배포 금지)`` -> ````
    ``(출처=청주시)`` -> ````
    """
    
    text = re.sub(r"\(출처?=?.+\)|\(출처 ?= ?.+\) |\[[^=]+=[^\]]+\)|\([^=]+=[^\)]+\)|\(사진 ?= ?.+\) |\(자료 ?= ?.+\)| \(자료사진\) |사진=.+기자 ", "", text).strip()
    return text


def remove_newsis(text):

    text = re.sub(r"\[[^]]+?=\s*뉴시스\]", "", text)

    return text


def remove_newsis_mark(text):

    text = re.sub(r"\[[^]]+?=\s*뉴시스\]", "", text)

    return text



# 첫번째에 = 이 오는경우
def removefirst_one(text):
    text = text.strip()
    if text[0] =='=':
        text = text[1:]
    return text

def newsisPreprocessing(text):
    try:
        text = text.split('기자 = ')[1]
    except Exception as e:  
        try:
            text = text.split('특파원 = ')[1]
        except Exception as e:
            try:
                text = text.split('리포터 = ')[1]
            except Exception as e:
                print('예외가 발생했습니다.', e)
                print(text)
                return ""

    text = replace_html_entities(text)
    text = remove_email_one(text)
    text = remove_html_one(text)
    text = remove_photo_info_one(text)
    text = remove_press_one(text)
    text = remove_newsis(text)
    text = removefirst_one(text)
    text = text.replace("◎공감언론 뉴시스", "")
    return text.strip()



if __name__ == '__main__':
    text = '''<p><img src="https://image.newsis.com/2024/10/30/NISI20241030_0020578257_web.jpg?rnd=20241030112046"/></p><br /><br /><br />[서울=뉴시스]신재현 기자 = 더불어민주당이 30일 한동훈 국민의힘 대표 취임 100일 기자회견을 두고 &quot;국민 물음에 답하지 못했다&quot;며 &quot;울림도 알맹이도 없었다&quot;고 혹평했다. <br /><br />조승래 수석대변인은 이날 서면브리핑을 통해 &quot;한 대표가 정작 국민의 물음에는 분명히 답하지 못했다&quot;며 &quot;김건희 여사 국정농단 게이트를 제대로 넘어서지 않고 변화와 쇄신을 말할 수는 없다&quot;고 밝혔다. <br /><br />조 수석대변인은 &quot;김건희 여사 국정농단 의혹에 대해 국민께서 요구하시는 것은, 엄정한 수사로 진상을 철저히 파헤쳐서 법과 원칙에 따라 처리하라는 것&quot;이라고 말했다. <br /><br />이어 &quot;명품백 수수, 주가조작 등 온갖 의혹에 면죄부만 발급해온 검찰은 이미 신뢰를 잃었다. 바로 그 때문에 국민 대다수가 특검을 요구하는 것&quot;이라고 덧붙였다. <br /><br />조 수석대변인은 &quot;한동훈 대표는 특검에 대해 머뭇거리기만 할 뿐 분명하게 답하지 못한다&quot;며 &quot;특검 말고는 김건희 여사 문제를 국민께서 납득할 수준으로 풀 방법이 없다&quot;고 강조했다. <br /><br />그러면서 &quot;한 대표는 미봉책으로 변죽만 울리는 꼼수를 중단하길 바란다&quot;고 했다. <br /><br />한 대표는 이날 국회에서 당대표 취임 100일 기자회견을 열고 김 여사 등 대통령 친인척을 감찰하기 위한 특별감찰관 추진과 관련해 &quot;김 여사에 대한 우려와 걱정이 있다&quot;며 관철 의지를 밝혔다. 그러나 &#039;김건희 특검&#039;에 대해서는 말을 아꼈다.<br />
◎공감언론 뉴시스 again@newsis.com'''
    print()
    print(newsisPreprocessing(text))
    print()
