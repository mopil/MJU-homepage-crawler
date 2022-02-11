from bs4 import BeautifulSoup
from datetime import datetime
import telegram
from selenium import webdriver

token = ''
chat_id = '@hu_homepage_crawler'

def set_hu_driver(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.get(url)

    # additional action
    driver.switch_to.frame('mainFrm')
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.close()
    return soup


def crawling(soup):
    result = []
    for tag in soup.select('a'):
        title = tag.text.strip()
        if len(title) >= 7:
            result.append([title])
    pattern = datetime.today().strftime("%Y.%m")
    i = 0
    for tag in soup.select("td"):
        if pattern in str(tag):
            date = tag.text.strip()
            result[i].append(date)
            i += 1
    return result


def crawling_archien(soup):
    result = []
    soup = set_hu_driver(archien_url)
    for tag in soup.select('.text'):
        result.append([tag.text])
    i = 0
    for tag in soup.select("td"):
        if len(str(tag.text)) == 10:
            date = tag.text.strip()
            result[i].append(date)
            i += 1
    return result

def make_message(result, homepage_title):
    today = datetime.today().strftime("%Y.%m.%d")
    message = f'\n{homepage_title}'

    message_exist = False
    for notice in result:
        if notice[1] == today:
            message += f'\n{notice[0]}\n'
            message_exist = True
    if not message_exist:
        message += "\n새 글이 없습니다.\n"
    return message


def send_telegram(token, chat_id, message):
    my_bot = telegram.Bot(token)
    my_bot.sendMessage(chat_id=chat_id, text=message)
    print("send_telegram_message is called")

message = f'홍익대학교 {datetime.today().strftime("%Y.%m.%d")} 새 글\n'
student_url = 'https://sejong.hongik.ac.kr/contents/www/cor/studentsno.html'
soup = set_hu_driver(student_url)
result_student = crawling(soup)
message += make_message(result_student, f"학생공지{student_url}")

archien_url = 'https://archien.hongik.ac.kr/dept/0401.html'
soup = set_hu_driver(archien_url)
result_archien = crawling_archien(soup)
message += make_message(result_archien, f"건축공학과 공지\n{archien_url}")

send_telegram(token, chat_id, message)