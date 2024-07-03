import requests
from bs4 import BeautifulSoup
from preprocessNews import removeAll

def entertainRankingURL(count = 5):
    url = 'https://entertain.naver.com/ranking/page.json?&type=hit_total'
    response = requests.get(url)
    html = response.json()['newsListHtml']
    soup = BeautifulSoup(html, 'html.parser')
    url = soup.find_all('a',class_ ='tit', limit = count)
    return url

def find_entertain_xhr(url):
    result = 'https://api-gw.entertain.naver.com/news/article/'
    url_component = url.split('/')
    result += url_component[-2]+'/'+url_component[-1]
    return result


def entertainComponent(xhr_url):
    response = requests.get(xhr_url)
    
    result = response.json()['result']['articleInfo']['article']
    entertain_title = result['title']
    entertain_contents = result['content']

    soup = BeautifulSoup(entertain_contents,'html.parser')
    entertain_contents = list(map(str, soup.contents))  
    entertain_contents = removeAll(entertain_contents)
    return entertain_title, entertain_contents, '연예'


def entertainNews(count = 5):
    if count > 30:
        count = 30
    if count == 0:
        return None
    urls =entertainRankingURL(count)
    result = []
    for url in urls[:count]:
        xhr_url = find_entertain_xhr(url['href'])
        title, content, section = entertainComponent(xhr_url)
        result.append({'url' : url['href'],'title' : title, 'content' : content, 'section': section})
    return result

if __name__ =="__main__":
    print(entertainNews())
