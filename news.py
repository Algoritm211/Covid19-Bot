from bs4 import BeautifulSoup
import urllib.request
import datetime
from urllib.request import urlopen, Request
# from pprint import pprint
class News:

    def __init__(self, reg_url, headers={'User-Agent': 'Safari/537.3'}):
        self.headers = headers
        self.reg_url = reg_url
        self.req_1 = Request(url=self.reg_url, headers=self.headers)
        self.html = urlopen(self.req_1).read()
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.results = []

    def get_news(self):
        pass

    def present_news(self):
        show_news = ''
        result = []
        now = datetime.datetime.now()
        date = now.strftime('%d-%m-%Y, %H:%M')
        for item in self.results[::]:
            show_news = f'Информация по населенному пункту <b>{item["reg"]}</b>\n\nВыявлено заражений:<code> {item["active"]}</code>\n ' +\
                        f'\nВыздоровели: <code>{item["today"]}</code>\n\n<i>Данные от {date}</i>'
            result.append(show_news)
        return result

class CoronaUkrCity(News):

    def get_news(self):
        news = self.soup.find_all(name='p')
        data = []
        for i in news[6:31:]:
            data.append(i.get_text().split('—'))
        for item in data:
            try:
                reg = item[0].replace(u'\xa0', u' ')
                active = item[1].split()[0]
                today = item[1].split()[1][1::]
                # if 'Киевская' in item or 'Харьковская' in item or 'Днепропетровская' in item or 'Закарпатская ' in item:
                self.results.append({
                'reg':reg,
                'active':active,
                'today':today
                })
            except:
                continue

    def get_cities(self):
        regions = []
        news = self.soup.find_all(name='p')
        news = self.soup.find_all(name='p')
        data = []
        for i in news[6:31:]:
            data.append(i.get_text().split('—'))
        for item in data:
            try:
                reg = item[0].replace(u'\xa0', u' ')
                # if 'Киевская' in item or 'Харьковская' in item or 'Днепропетровская' in item or 'Закарпатская ' in item:
                regions.append(reg)
            except:
                continue
        return regions



def get_news_ukr_cities():
    news = CoronaUkrCity('https://nv.ua/amp/koronavirus-v-ukraine-karta-novosti-ukrainy-50075556.html')
    news.get_news()
    return news.present_news()
# get_news_ukr_cities()
def get_cities_to_make_keyboard():
    news = CoronaUkrCity('https://nv.ua/amp/koronavirus-v-ukraine-karta-novosti-ukrainy-50075556.html')
    return news.get_cities()
# print(get_cities_to_make_keyboard())

# print(get_news_ukr_cities())

class CoronaNews(News):

    def get_news(self):
        news = self.soup.find_all(name='div', attrs={'class':'CardsList-wrapper CardsList-wrapper_theme_light'})
        for item in news:
            title = item.find(name='a').get('data-vr-contentbox')
            link = 'https://hromadske.ua' + item.find(name='a').get('href')
            self.results.append({
            'title': title,
            'link':link
            })

    def present_news(self):
        show_news = '----------\n' + '📍<b>Последние новости о коронавирусе в Укранине и мире</b>📍\n' + '----------\n'
        for item in self.results[::]:
            show_news += f'<a href="{item["link"]}"> {item["title"]}</a>\n\n'
        return show_news


def get_corona_news():
    news = CoronaNews('https://hromadske.ua/ru/tags/koronavirus')
    news.get_news()
    return news.present_news()

# print(get_corona_news())
