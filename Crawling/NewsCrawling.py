import requests
from bs4 import BeautifulSoup
from preprocessNews import removeAll


def find_url(url):
    url_split = url.split('/')
    url_x = url_split[-1].split('?sid=')
    result_url = 'https://news.naver.com/main/read.nhn?mode=LSD&mid=sec&&oid='+url_split[-2]+'&aid='+url_x[0]

    return result_url

##분야별 주요뉴스 크롤링
def mainNewsURL():
    url = 'https://news.naver.com/section/template/SECTION_MAINNEWS'
    r= requests.get(url)
    content = r.json()
    section_mainnews = content['renderedComponent']['SECTION_MAINNEWS']
    soup = BeautifulSoup(section_mainnews,'html.parser')
    urls =  soup.find_all('a',class_='rl_coverlink',limit=15)
    return urls




def returnSoup(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content,'html.parser')
    return soup


def soupFindNaverVideo(soup):
    video = soup.find('div',class_='vod_player_wrap _VIDEO_AREA_WRAP')

    if video:
        return True
    return False


def soupNaverComponent(soup):
    # title = soup.find('h2',class_='media_end_head_headline').text 
    content = soup.find('article',class_='go_trans _article_content').contents
    content = list(map(str,content))
    category = soup.find('em',class_ = 'media_end_categorize_item').text
    # return title, content, category
    return content, category

def News(count = 5):
    if count > 15:
        count = 15
        
    if count == 0:
        return []
    try:
        tags = mainNewsURL()
        news = [] 

        for tag in tags:
            news_url =find_url(tag['href'])

            soup = returnSoup(news_url)

            if soupFindNaverVideo(soup):
                continue

            try:
                content, section = soupNaverComponent(soup)
                content = removeAll(content)
            except:
                continue
            
            news.append({'url' : tag['href'],'content' : content, 'section': section})
            

            if len(news) == count:
                break
    except:
        news = News(count)
    return news


if __name__ =='__main__':
    result = News(10)
    print(len(result))