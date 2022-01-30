import time
import telegram
from telegram.ext import Updater, CommandHandler
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import schedule

storage = []
api_key = ''
chat_id = ''

prefix_url = 'http://jw4.mju.ac.kr/user/'

my_bot = telegram.Bot(api_key)


def chrome_driver_setting():
    options = Options()
    options.add_argument('headless')  # headless 모드 설정
    options.add_argument("window-size=1920x1080")  # 화면크기(전체화면)
    options.add_argument("disable-gpu")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")

    # 속도 향상을 위한 옵션 해제
    prefs = {'profile.default_content_setting_values': {'cookies': 2, 'images': 2, 'plugins': 2, 'popups': 2,
                                                        'geolocation': 2, 'notifications': 2,
                                                        'auto_select_certificate': 2, 'fullscreen': 2, 'mouselock': 2,
                                                        'mixed_script': 2, 'media_stream': 2, 'media_stream_mic': 2,
                                                        'media_stream_camera': 2, 'protocol_handlers': 2,
                                                        'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
                                                        'push_messaging': 2, 'ssl_cert_decisions': 2,
                                                        'metro_switch_to_desktop': 2, 'protected_media_identifier': 2,
                                                        'app_banner': 2, 'site_engagement': 2, 'durable_storage': 2}}
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome('chromedriver', options=options)
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


def auto_crawling():
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



'''
텔레그램 봇 설정
[명령어]
/get = 수동으로 새 글 긁어오기
/reset = storage 초기화
'''

updater = Updater(api_key)
updater.dispatcher.stop()
updater.job_queue.stop()
updater.stop()


def manual_crawling(bot, update):
    auto_crawling()


def reset_storage(bot, update):
    storage.clear()
    message = '저장 공간을 모두 리셋 했습니다'
    my_bot.sendMessage(chat_id=chat_id, text=message)


updater.dispatcher.add_handler(CommandHandler("get", manual_crawling))
updater.dispatcher.add_handler(CommandHandler("reset", reset_storage))

# 명령어로 테스트 하기
#updater.start_polling()
#updater.idle()


# init
storage = get_all_articles()

schedule.every(1).seconds.do(auto_crawling)

while True:
    schedule.run_pending()
    time.sleep(1)


