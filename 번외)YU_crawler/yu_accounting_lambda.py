import requests
from bs4 import BeautifulSoup
import datetime
import telegram

'''
회계세무학과
'''

def lambda_handler(event, context):
    prefix_url = 'https://acc.yu.ac.kr/acc/notice/notice.do'
    MAX_ARTICLE = 15
    response = requests.get(prefix_url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')

    api_key = 0
    chat_id = '@yu_homepage_crawler'

    my_bot = telegram.Bot(api_key)

    titles, links, dates = list(), list(), list()

    for item in soup.select('.b-title-box > a'):
        title, link = item['title'], prefix_url + item['href']
        if title not in titles:
            titles.append(title)
        if 'comment' not in link:
            links.append(link)

    for item in soup.select('.b-date'):
        dates.append(item.text.strip())

    today = datetime.datetime.now().strftime('%Y.%m.%d')
    message = f'영남대학교 ★회계세무학과★ {today} 새 글'
    count = 0
    for i in range(MAX_ARTICLE):
        if dates[i] == today:
            message += f'\n[{titles[i]}]\n{links[i]}'
            count += 1
    if count == 0:
        message += "\n오늘은 새로운 글이 없네요"
    my_bot.sendMessage(chat_id=chat_id, text=message)
