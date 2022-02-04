import starter as st
import telegram
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
    
    # telegram message sending
    api_key = '5251720307:AAEioDUzN6YsqRYE034soQq8N3-DJ8BSX28'
    chat_id = '@mju_computer_crawling' #1413972042 #my_bot
    my_bot = telegram.Bot(api_key)
    
    message = f'명지대학교 컴퓨터공학과 홈페이지\n{datetime.today().strftime("%Y/%m/%d")} 새 글'
    if not result:
        message = f'{datetime.today().strftime("%Y/%m/%d")}\n새 글이 없습니다.'
    else:
        for a in result:
            message += f'\n{a[0]}\n{a[1]}'
    my_bot.sendMessage(chat_id=chat_id, text=message)
