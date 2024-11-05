import requests
from bs4 import BeautifulSoup
from preprocessNews import newsisPreprocessing


def findTopNews(headline =7, politic =7, world = 7, economy = 7 , IT = 7 , society = 7 , sports = 7, entertain = 7, culture = 7):

    categorys = {'종합':'https://www.newsis.com/politic/?cid=10300','정치':'https://www.newsis.com/politic/?cid=10300','국제':'https://www.newsis.com/world/?cid=10100',
                 '경제':'https://www.newsis.com/economy/?cid=10400', 'IT·바이오':'https://www.newsis.com/health/?cid=13100','사회':'https://www.newsis.com/society/?cid=10200',
                 '스포츠':'https://www.newsis.com/sports/?cid=10500', '연예':'https://www.newsis.com/entertainment/?cid=10600','문화' : 'https://www.newsis.com/culture/?cid=10700'}
    
    remove_category = set(['광장', '포토', '위클리뉴시스'])
    #  생활, IT
    
    num_list = [headline, politic, world, economy , IT , society , sports, entertain, culture]
    for idx, num in enumerate(num_list):
        if num >7:
            num_list[idx] = 7
        elif num<0:
            num_list[idx] = 0

    base_url = 'https://www.newsis.com'

    num = 5
    news_set =set()
    for (category,url), num in zip(categorys.items(), num_list):

        try:
            r= requests.get(url)
            soup = BeautifulSoup(r.text,'html.parser')
            soup2 = soup.find('div', {'data-name': category})
            urls  = soup2.find_all('div', class_='txtCont')
        except Exception as e:
            print( category," 뉴스 가져오는데 오류 발생:", str(e))
            continue
        
        cate = category
        for i in range(num):
            news_url = base_url+urls[i].find('a').get('href') 
            # print(news_url)
            if category == '종합':
                r2 = requests.get(news_url)
                soup3 = BeautifulSoup(r2.text,'html.parser')
                cate = soup3.find('p', class_ = 'tit')
                cate = cate.text
            
            if cate and (cate not in remove_category):
                news_set.add((cate,news_url))
    return news_set

def findNewsContents(news_list):

    RSS = {'속보': 'https://www.newsis.com/RSS/sokbo.xml', '정치': 'https://www.newsis.com/RSS/politics.xml','국제': 'https://www.newsis.com/RSS/international.xml',
 '경제': 'https://www.newsis.com/RSS/economy.xml',  '금융': 'https://www.newsis.com/RSS/bank.xml', '산업': 'https://www.newsis.com/RSS/industry.xml',
 '사회': 'https://www.newsis.com/RSS/society.xml', 'IT·바이오': 'https://www.newsis.com/RSS/health.xml', '수도권': 'https://www.newsis.com/RSS/met.xml',
 '지방': 'https://www.newsis.com/RSS/country.xml', '스포츠': 'https://www.newsis.com/RSS/sports.xml', '연예': 'https://www.newsis.com/RSS/entertain.xml',
 '문화': 'https://www.newsis.com/RSS/culture.xml', '광장': 'https://www.newsis.com/RSS/square.xml', '포토': 'https://www.newsis.com/RSS/photo.xml',
 '위클리뉴시스': 'https://www.newsis.com/RSS/newsiseyes.xml'}

    change_category = {'정치':'정치', '국제':'세계', '경제':'경제', '금융':'경제', '산업':'경제', '사회' :'사회', 'IT·바이오':'IT', '수도권':'사회',
        '지방':'사회', '스포츠':'스포츠', '연예':'연예', '문화':'문화'}
    

    result_list = []
    for category, link in news_list:
        response= requests.get(RSS[category])
        soup = BeautifulSoup(response.text, 'lxml-xml')
        for idx, news_link in enumerate(soup.select('item > link')):
            if link == news_link.text.strip():
                # print(link)
                content = newsisPreprocessing(soup.find_all('description')[idx+1].text)
                if content:
                    result_list.append({'url':link, 'section': change_category[category], 'content' : content})
                break
    return result_list
if __name__=='__main__':
    for i in range(8):
        print(i)
        li =[0]*8
        li[i] = 1
        news_list =findTopNews(*li)
    # news_list =findTopNews(1,1,1,1,1,1,1,1)
    # for i in findNewsContents(news_list):
    #     print(i)
    