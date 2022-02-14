import requests
from bs4 import BeautifulSoup
from datetime import datetime
import telegram


def crawling_yu_common_notice(url):
    prefix_url = url
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    result = []
    for tag in soup.select('.b-title-box > a'):
        title, link = tag['title'], prefix_url + tag['href']
        result.append([title, link])
    i = 0
    for tag in soup.select("td"):
        # 날짜를 찾는 로직 == 날짜 2022.01.10 10자리 수로 판단
        if len(str(tag.text)) == 10:
            date = tag.text.strip()
            try:
                result[i].append(date)
            except IndexError:
                continue
            i += 1

    final = []
    today = datetime.today().strftime("%Y.%m.%d")
    for article in result:
        try:
            if today == article[2]:
                final.append(article)
        except IndexError:
            continue
    return final


def send_telegram(token, chat_id, message):
    my_bot = telegram.Bot(token)
    my_bot.sendMessage(chat_id=chat_id, text=message)


def make_message(result):
    message = ""
    for notice in result:
        message += str(notice[0]) + '\n' + str(notice[1]) + '\n\n'
    return message


total_message = f'{datetime.today().strftime("%Y-%m-%d")} 영남대학교 공지 사항 알림\n'

arr = {
    "◎학사 공지◎": 'https://www.yu.ac.kr/main/bachelor/bachelor-guide.do',
    "◎회계◎": 'https://econ.yu.ac.kr/econ/dept/undergrad-notice.do',
    "◎경제◎": 'https://acc.yu.ac.kr/acc/notice/notice.do'
}

for title, url in arr.items():
    crawled_notice = crawling_yu_common_notice(url)
    message = f'{title}\n'
    if not crawled_notice:
        message += "새 글이 없습니다.\n\n"
    else:
        message += make_message(crawled_notice)
    total_message += message
send_telegram('5285266759:AAEh8TdTywytRORumvwbRghC4K9ww-Upy20','@yu_homepage_crawler',total_message)