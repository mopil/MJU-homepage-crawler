import requests
from bs4 import BeautifulSoup
import telegram
import datetime

prefix_url = 'http://www.mju.ac.kr'
response = requests.get('http://www.mju.ac.kr/mjukr/257/subview.do')
soup = BeautifulSoup(response.content, 'html.parser')


titles, links = list(), list()

result = []
for tag in soup.select('.artclLinkView'):
    title, link = tag.text, prefix_url + tag['href']
    if "새글" in title:
        result.append((title, link))

api_key = ''
chat_id = '@mju_computer_crawling'

my_bot = telegram.Bot(api_key)

message = f'{datetime.datetime.today().strftime("%Y.%m.%d")} 명지대 학사 공지'
if not result:
    message += '새 글이 없습니다.'

for new in result:
    title = new[0].replace("새글", "").strip()
    message += f'\n{title}\n{new[1]}\n'

my_bot.sendMessage(chat_id=chat_id, text=message)
