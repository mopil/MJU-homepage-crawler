import pymysql
import requests
from bs4 import BeautifulSoup
from datetime import datetime

host = ''
port = 3306
user = ''
password = ''
db = ''


def make_message2(result, homepage_title):
    today = datetime.today().strftime("%Y.%m.%d")
    message = f'\n{homepage_title}'

    message_exist = False
    for notice in result:
        try:
            if notice[2] == today:
                message += f'\n{notice[0]}\n{notice[1]}\n'
                message_exist = True
        except IndexError:
            pass
    if not message_exist:
        message += "\n새 글이 없습니다.\n"

    return message


def make_message(result, homepage_title):
    message = f'\n{homepage_title}'

    message_exist = False
    for notice in result:
        try:
            message += f'\n{notice[0]}\n{notice[1]}\n'
            message_exist = True
        except IndexError:
            pass
    if not message_exist:
        message += "\n새 글이 없습니다.\n"

    return message


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
        "◎학사 공지◎": 'http://www.mju.ac.kr/mjukr/257/subview.do',
        "◎일반 공지◎": 'http://www.mju.ac.kr/mjukr/255/subview.do',
        "◎장학 공지◎": 'http://www.mju.ac.kr/mjukr/259/subview.do',
    }

    result_list = []
    for url in url_list.values():
        crawled_list = crawling_school_notice(url)
        result_list.append(db_check(crawled_list))
    total_message = f'{datetime.today().strftime("%Y-%m-%d")} 명지대학교 공지사항 알림'
    t = 0
    for title in url_list.keys():
        try:
            total_message += make_message(result_list[t], title)
            t += 1
        except IndexError:
            pass

    if t != 3:
        token = ''
        channal = '#test'

        response = requests.post("https://slack.com/api/chat.postMessage",
                                 headers={"Authorization": "Bearer " + token},
                                 data={"channel": channal, "text": total_message}
                                 )
        print('lambda executed.')


def in_db(title, result_from_db):
    for check in result_from_db:
        if title == check[0]:
            return True
    return False


def db_check(crawled_list):
    database = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        db=db)

    cursor = database.cursor()

    # 데이터베이스에서 데이터 전체 조회
    cursor.execute("SELECT title FROM announcement")
    database.commit()
    result_from_db = cursor.fetchall()

    final_result = []
    for data in crawled_list:
        title = data[0]
        if not in_db(title, result_from_db):
            insert_sql = f"INSERT INTO announcement(title) VALUES ('{title}');"
            cursor.execute(insert_sql)
            final_result.append(data)
    database.commit()
    return final_result

