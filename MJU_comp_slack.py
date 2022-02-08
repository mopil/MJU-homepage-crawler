import starter as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver.common.by import By


def set_mju_comp_driver(url):
    driver = st.start_drive()
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


def lambda_handler(event, context):
    message = f'{datetime.today().strftime("%Y-%m-%d")} 명지대학교'
    soup = set_mju_comp_driver('http://jw4.mju.ac.kr/user/cs/index.action')
    result_comp = crawling_comp(soup)
    message += make_message(result_comp, "컴퓨터공학과", "comp")
    token = ''
    channal = '#test'

    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channal, "text": message}
                             )
