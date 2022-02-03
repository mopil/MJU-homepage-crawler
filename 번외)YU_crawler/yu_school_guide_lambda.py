'''
학사공지
'''
import requests
from bs4 import BeautifulSoup
import datetime
import telegram


def lambda_handler(event, context):

    prefix_url = 'https://www.yu.ac.kr/main/bachelor/bachelor-guide.do'
    MAX_ARTICLE = 10
    response = requests.get(prefix_url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')

    api_key = 0
    chat_id = '@yu_homepage_crawler'

    my_bot = telegram.Bot(api_key)

    titles, links, dates = list(), list(), list()
    for tag in soup.select('.b-title-box > a'):
        title = tag.select('span')[1].text
        link = prefix_url + tag['href']
        titles.append(title)
        links.append(link)

    for date in soup.select('.b-date'):
        dates.append(date.text)

    today = datetime.datetime.now().strftime('%Y.%m.%d')

    message = f'영남대학교 ◆학사공지◆ {today} 새 글'

    count = 0
    for i in range(MAX_ARTICLE):
        if dates[i] == today:
            message += f'\n[{titles[i]}]\n{links[i]}'
            count += 1
    if count == 0:
        message += "\n오늘은 새로운 글이 없네요"
    my_bot.sendMessage(chat_id=chat_id, text=message)



