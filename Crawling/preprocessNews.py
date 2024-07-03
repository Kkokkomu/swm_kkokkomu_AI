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





if __name__ == '__main__':
    import TransURL
    print(remove_photo_info(['(출처=청주시),(출처 = 청주시)']))

    # link = 'https://news.nate.com/view/20240621n10697?mid=n1008'
    # link = 'https://news.nate.com/view/20240621n03701?mid=n1008'

    # news_name, news_contents = TransURL.newsContents(link)
    # print()
    # print('제목 : ',news_name)
    # print()
    # news_contents = re.sub(r'다\.','다.\n ',news_contents)
    # news_contents = news_contents.split('\n')

    # news_contents = removeAll(news_contents)
    # # print(news_contents)
    # for i in news_contents:
    #     print(i)

    # print()