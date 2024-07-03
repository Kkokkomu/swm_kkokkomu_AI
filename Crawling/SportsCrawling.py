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

    result = response.json()['result']['articleInfo']['article']
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
        title, content, section = sportsComponent(xhr_url)
        result.append({'url' : url['href'],'title' : title, 'content' : content, 'section': section})
    
    return result
