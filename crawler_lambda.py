import starter as st
import telegram
from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver.common.by import By

api_key = '5251720307:AAEioDUzN6YsqRYE034soQq8N3-DJ8BSX28'
chat_id = 1413972042

prefix_url = 'http://jw4.mju.ac.kr/user/'

my_bot = telegram.Bot(api_key)


def chrome_driver_setting():
    driver = st.start_drive()
    driver.get('http://jw4.mju.ac.kr/user/cs/index.action')
    driver.switch_to.frame('index_frame')
    driver.find_element(By.XPATH,
                        '//*[@id="pageRightT"]/div[2]/div[1]/div/ul/li[1]/ul/div/div/table/tbody/tr/td/table[1]/tbody/tr/td/a/img').click()
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.close()
    return soup


def get_all_articles():
    soup = chrome_driver_setting()
    result = []
    for i in soup.select("td > a"):
        title, link = i.text.strip(), prefix_url + i['href']
        if title == '':
            continue
        else:
            result.append((title, link))
    return result


def get_new_articles():
    soup = chrome_driver_setting()
    result = []
    # 새로운 글만 가져온다 로직 : new 아이콘이 있는 글만 가져오기
    for tag in soup.select("td > a"):
        for sub_tag in tag.descendants:
            if "img" in str(sub_tag):
                title, link = tag.text.strip(), prefix_url + tag['href']
                result.append((title, link))
    return result


def auto_crawling(storage):
    temp = get_new_articles()
    message = f'명지대학교 컴퓨터공학과 홈페이지\n{datetime.today().strftime("%Y/%m/%d")} 새 글'
    count = 0
    for a in temp:
        if a not in storage:
            storage.append(a)
            message += f'\n{a[0]}\n{a[1]}'
            count += 1
    if count == 0:
        message = '새 글이 없습니다'
    my_bot.sendMessage(chat_id=chat_id, text=message)


def lambda_handler(event, context):
    storage = get_all_articles()

    auto_crawling(storage)