import pymysql
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def make_message(result, homepage_title):
    message = f'\n{homepage_title}'

    message_exist = False
    for notice in result:
        try:
            message += f'\n{notice[0]}\n{notice[1]}\n'
            message_exist = True
        except IndexError:
            pass

    return message, message_exist


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
        if i >= len(result): break
        if pattern in str(tag):
            result[i].append(tag.text)
            i += 1

    for new in result:
        new[0] = new[0].replace("새글", "").strip()

    return result


def lambda_handler(event, context):
    # main logic
    url_list = {
        "학사": 'http://www.mju.ac.kr/mjukr/257/subview.do',
        "일반": 'http://www.mju.ac.kr/mjukr/255/subview.do',
        "장학": 'http://www.mju.ac.kr/mjukr/259/subview.do',
    }

    result_list = []
    for category, url in url_list.items():
        crawled_list = crawling_school_notice(url)
        result_list.append(db_check(category, crawled_list))
    total_message = f'{datetime.today().strftime("%Y-%m-%d")} 명지대학교 공지사항 알림'
    t, message_check = 0, 0
    for title in url_list.keys():
        temp_message, message_result = make_message(result_list[t], title)
        if message_result:
            total_message += temp_message
            t += 1
        else:
            message_check += 1

    if message_check != 3:
        token = ''
        channal = '#test'

        response = requests.post("https://slack.com/api/chat.postMessage",
                                 headers={"Authorization": "Bearer " + token},
                                 data={"channel": channal, "text": total_message}
                                 )
        print('lambda executed.')
    else:
        print("no new articles ")


def in_db(title, result_from_db):
    for check in result_from_db:
        if title == check[0]:
            return True
    return False


def db_check(category, crawled_list):
    database = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        db=db)

    cursor = database.cursor()

    # 데이터베이스에서 데이터 전체 조회
    today = datetime.today().strftime("%Y-%m-%d")
    cursor.execute(f"SELECT title FROM announcement")

    database.commit()
    result_from_db = cursor.fetchall()

    final_result = []
    for data in crawled_list:
        title = data[0]
        if not in_db(title, result_from_db):
            insert_sql = f"INSERT INTO announcement(category, title) VALUES (%s, %s);"
            insert_data = (category, title)
            cursor.execute(insert_sql, insert_data)
            final_result.append(data)
            database.commit()
    return final_result

