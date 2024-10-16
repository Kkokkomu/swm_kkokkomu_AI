import requests
from bs4 import BeautifulSoup
from preprocessNews import removeAll

def findSportsRankingURL(count = 10):
    url = 'https://sports.news.naver.com/ranking/index'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    url = soup.find_all('a',class_='title',limit=count)
    return url

def find_sports_xhr(url):
    result = 'https://api-gw.sports.naver.com/news/article/'
    url_component = url.split('/')
    result += url_component[-2]+'/'+url_component[-1]
    return result


def sportsComponent(xhr_url):
    response = requests.get(xhr_url)
    if response.status_code != 200:
        print('This news is none')
        return None
    ## 오류 발생
    try:
        result = response.json()['result']['articleInfo']['article']
    except:
        return None
    sports_title = result['title']
    sports_contents = result['content']

    soup = BeautifulSoup(sports_contents,'html.parser')

    # 이미지 태그 들어간것 전부 제거
    image_texts = soup.find_all('em',class_ = 'img_desc')
    for image_text in image_texts:
        image_text.decompose()

    
    sports_contents = map(str, soup.contents)  
    sports_contents = removeAll(sports_contents)
    return sports_title, sports_contents, '스포츠'


def sportsNews(count = 10):
    if count > 20:
        count = 20
    if count == 0:
        return None
    urls =findSportsRankingURL(count)
    result = []
    for url in urls:
        xhr_url = find_sports_xhr(url['href'])
        print(xhr_url)
        components = sportsComponent(xhr_url)
        if components == None:
            continue
        title, content, section = components
        result.append({'url' : url['href'],'title' : title, 'content' : content, 'section': section})
    
    return result

import json 
if __name__ =='__main__':

    result = sportsNews(20)
    result_dic = {i : x for i,x in enumerate(result)}
    with open('./data.json','w', encoding='UTF-8') as json_file:
        json.dump(result_dic, json_file,indent='\t',ensure_ascii=False)
    
    print(len(result))
