import requests
from bs4 import BeautifulSoup
from datetime import datetime


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


# main logic
time = datetime.today().strftime("%Y-%m-%d")
url_list = {
    "◎학사 공지◎":'http://www.mju.ac.kr/mjukr/257/subview.do',
    "◎일반 공지◎":'http://www.mju.ac.kr/mjukr/255/subview.do',
    "◎장학 공지◎":'http://www.mju.ac.kr/mjukr/259/subview.do',
}

result_list = []
for url in url_list.values():
    result_list.append(crawling_school_notice(url))
total_message = f'{datetime.today().strftime("%Y-%m-%d")} 명지대학교 공지사항 알림'
t = 0
for title in url_list.keys():
    total_message += make_message(result_list[t], title)
    t += 1


token = ''
channal = '#test'

response = requests.post("https://slack.com/api/chat.postMessage",
                         headers={"Authorization": "Bearer " + token},
                         data={"channel": channal, "text": total_message}
                         )
print(f'{time} lambda executed.')
