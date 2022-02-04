import starter as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium.webdriver.common.by import By


def lambda_handler(event, context):
    # driver settings
    driver = st.start_drive()
    driver.get('http://jw4.mju.ac.kr/user/cs/index.action')
    driver.switch_to.frame('index_frame')
    driver.find_element(By.XPATH,
                        '//*[@id="pageRightT"]/div[2]/div[1]/div/ul/li[1]/ul/div/div/table/tbody/tr/td/table[1]/tbody/tr/td/a/img').click()
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.close()

    result = []

    # new articles crawling
    prefix_url = 'http://jw4.mju.ac.kr/user/'
    for tag in soup.select("td > a"):
        for sub_tag in tag.descendants:
            if "img" in str(sub_tag):
                title, link = tag.text.strip(), prefix_url + tag['href']
                result.append((title, link))


    message = f'명지대학교 컴퓨터공학과 홈페이지\n{datetime.today().strftime("%Y/%m/%d")} 새 글'
    if not result:
        message += '\n새 글이 없습니다.'
    else:
        for a in result:
            message += f'\n{a[0]}\n{a[1]}'
    token = 'xoxb-2901743260471-3055750016835-hOj09tLdbXky7V9WsWnYhmLh'
    channal = '#컴퓨터공학과'

    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer " + token},
                             data={"channel": channal, "text": message}
                             )