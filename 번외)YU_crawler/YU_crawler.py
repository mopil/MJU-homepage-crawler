import requests
from bs4 import BeautifulSoup
from datetime import datetime
import telegram

api_key = ''
chat_id = '@mju_computer_crawling'


def make_message(result, homepage_title, type="default"):
    if type == "comp":
        today = datetime.today().strftime("%Y-%m-%d")
    else:
        today = datetime.today().strftime("%Y.%m.%d")
    message = f'\n{homepage_title}'

    message_exist = False
    for notice in result:
        if notice[2] == today:
            message += f'\n{notice[0]}\n{notice[1]}\n'
            message_exist = True
    if not message_exist:
        message += "\n새 글이 없습니다.\n"
    return message


def send_telegram(token, chat_id, message):
    my_bot = telegram.Bot(token)
    my_bot.sendMessage(chat_id=chat_id, text=message)
    print("send_telegram_message is called")


def crawling(url):
    prefix_url = url
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    titles, links, dates = list(), list(), list()

    for item in soup.select('.b-title-box > a'):
        title, link = item['title'], prefix_url + item['href']
        if title not in titles:
            titles.append(title)
        if 'comment' not in link:
            links.append(link)

    for item in soup.select('.b-date'):
        dates.append(item.text.strip())

    result = []
    for i in range(len(titles)):
        result.append([titles[i], links[i], dates[i]])
    return result


result_school_notice = crawling('https://www.yu.ac.kr/main/bachelor/bachelor-guide.do')
result_economic = crawling('https://econ.yu.ac.kr/econ/dept/undergrad-notice.do')
result_accounting = crawling('https://acc.yu.ac.kr/acc/notice/notice.do')
message = make_message(result_school_notice, "◎학사공지◎") + make_message(result_accounting, "◎회계◎") + make_message(result_economic, "◎경제◎")
send_telegram(api_key, chat_id, message)

