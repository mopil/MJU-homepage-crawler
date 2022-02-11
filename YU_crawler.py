import requests
from bs4 import BeautifulSoup
from datetime import datetime
import telegram
import boto3


class S3BucketManager:
    def __init__(self, id, key, bucket_name, file_name):
        self.file_name = file_name
        self.bucket_name = bucket_name
        self.s3 = boto3.resource(
            's3',
            aws_access_key_id=id,
            aws_secret_access_key=key
            )
        self.client = boto3.client(
            's3',
            aws_access_key_id=id,
            aws_secret_access_key=key
            )
        print("s3 bucket successfully connected.")

    def write_file(self, message, mode):
        with open(self.file_name, mode, encoding='utf-8') as f:
            f.write(message + "\n")
        self.client.upload_file(self.file_name, self.bucket_name, self.file_name)

    def read_file(self):
        obj = self.s3.Object(self.bucket_name, self.file_name)
        body = obj.get()["Body"].read()
        #print(f'{file_name} is successfully read.')
        return body.decode()

    def clear_file(self):
        self.write_file("", "w")
        print(f'{self.file_name} all data reset complete.')


def send_telegram(token, chat_id, message):
    my_bot = telegram.Bot(token)
    my_bot.sendMessage(chat_id=chat_id, text=message)
    print("send_telegram_message is called")


def crawling(url):
    prefix_url = url
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    titles, links, dates = list(), list(), list()

    for item in soup.select('.b-title-box > a'):
        title, link = item['title'], prefix_url + item['href']
        if title not in titles:
            titles.append(title)
        if 'comment' not in link:
            links.append(link)

    for item in soup.select('.b-date'):
        dates.append(item.text.strip())

    result = []
    for i in range(len(titles)):
        result.append([titles[i], links[i], dates[i]])
    return result


def duplication_filtering(s3_manager, crawled_result):
    filtered_result = []
    stored_notice = s3_manager.read_file()  # stored_notice = type : str
    for notice in crawled_result:
        title = notice[0]
        if title not in stored_notice:
            s3_manager.write_file(title, "a")
            filtered_result.append(notice)
    return filtered_result


def make_message(result):
    message = ""
    for notice in result:
        message += str(notice[0]) + '\n' + str(notice[1]) + '\n\n'
    return message


def main_logic(homepage_title, homepage_url, s3_manager):
    crawled_notice = crawling(homepage_url)
    filtered_notice = duplication_filtering(s3_manager, crawled_notice)
    if not filtered_notice:
        return "empty"
    else:
        return f'{homepage_title}\n' + make_message(filtered_notice)


api_key = ''
chat_id = '@yu_homepage_crawler'
id = ''
key = ''
bucket_name = "mju-announcements"
file_name = "tmp/YU_store.txt"
manager = S3BucketManager(id, key, bucket_name, file_name)
total_message = f'{datetime.today().strftime("%Y-%m-%d")} 영남대학교 공지 사항 알림\n'

arr = {
"◎학사 공지◎":'https://www.yu.ac.kr/main/bachelor/bachelor-guide.do',
"◎회계◎":'https://econ.yu.ac.kr/econ/dept/undergrad-notice.do',
"◎경제◎":'https://acc.yu.ac.kr/acc/notice/notice.do'
}
for homepage_title, homepage_url in arr.items():
    result = main_logic(homepage_title, homepage_url, manager)
    if result == "empty":
        print(f"{homepage_title} crawling result = no new notice.")
    else:
        message = f"새로운 공지\n" + result + '\n'
        send_telegram(api_key, chat_id, message)


