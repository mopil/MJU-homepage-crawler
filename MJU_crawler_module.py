from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver.common.by import By
import telegram
from selenium import webdriver
import requests

url = 'http://jw4.mju.ac.kr/user/cs/index.action'
api_key = ''
chat_id = '@mju_computer_crawling'


def set_driver(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.close()
    return soup


def set_mju_comp_driver(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.get(url)

    # additional action
    driver.switch_to.frame('index_frame')
    driver.find_element(By.XPATH,
                        '//*[@id="pageRightT"]/div[2]/div[1]/div/ul/li[1]/ul/div/div/table/tbody/tr/td/table[1]/tbody/tr/td/a/img').click()

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.close()
    return soup


def crawling_comp(soup):
    result = []
    # new articles crawling
    prefix_url = 'http://jw4.mju.ac.kr/user/'
    for tag in soup.select("td > a"):
        for sub_tag in tag.descendants:
            if "img" in str(sub_tag):
                title, link = tag.text.strip(), prefix_url + tag['href']
                result.append([title, link])

    pattern = datetime.today().strftime("%Y-%m")
    i = 0
    for tag in soup.select("td"):
        if pattern in str(tag):
            date = tag.text.strip()
            result[i].append(date)
            i += 1
    return result


def crawling_school_notice(url):
    prefix_url = 'http://www.mju.ac.kr'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    result = []
    for tag in soup.select('.artclLinkView'):
        title, link = tag.text, prefix_url + tag['href']
        if "새글" in title:
            result.append([title, link])
    pattern = datetime.today().strftime("%Y.%m")
    i = 0
    for tag in soup.select('._artclTdRdate'):
        if pattern in str(tag):
            result[i].append(tag.text)
            i += 1

    for new in result:
        new[0] = new[0].replace("새글", "").strip()

    return result


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


# 컴퓨터공학과
soup_comp = set_mju_comp_driver(url)
result_comp = crawling_comp(soup_comp)

# 학사, 일반, 장학, 경력, 학생활동, 코로나
url_list = {
    "◎학사 공지◎":'http://www.mju.ac.kr/mjukr/257/subview.do',
    "◎일반 공지◎":'http://www.mju.ac.kr/mjukr/255/subview.do',
    "◎장학 공지◎":'http://www.mju.ac.kr/mjukr/259/subview.do',
    #"◎학생 활동 공지◎":'http://www.mju.ac.kr/mjukr/5364/subview.do',
    #"◎코로나 공지◎":'http://www.mju.ac.kr/mjukr/3860/subview.do'
}

result_list = []
for url in url_list.values():
    result_list.append(crawling_school_notice(url))
total_message = f'{datetime.today().strftime("%Y-%m-%d")} 명지대학교 공지사항 알림'
i = 0
for title in url_list.keys():
    total_message += make_message(result_list[i], title)
    i += 1

send_telegram(api_key, chat_id, total_message)
