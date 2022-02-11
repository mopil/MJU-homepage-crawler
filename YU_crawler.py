import sys
sys.path.append("C:\\dev\\MJU-homepage-announcer\module")

from datetime import datetime
from module.message_manager import send_telegram, make_message
from module.crawler import crawling_yu_notice
from module.s3_manager import S3Manager
from module.secret_keys import Tokens

bucket_name = "mju-announcements"
file_name = "tmp/YU_store.txt"

manager = S3Manager(Tokens.AWS_S3_ID, Tokens.AWS_S3_KEY, bucket_name, file_name)
total_message = f'{datetime.today().strftime("%Y-%m-%d")} 영남대학교 공지 사항 알림\n'

arr = {
    "◎학사 공지◎": 'https://www.yu.ac.kr/main/bachelor/bachelor-guide.do',
    "◎회계◎": 'https://econ.yu.ac.kr/econ/dept/undergrad-notice.do',
    "◎경제◎": 'https://acc.yu.ac.kr/acc/notice/notice.do'
}


def main_logic(homepage_title, homepage_url, s3_manager):
    crawled_notice = crawling_yu_notice(homepage_url)
    filtered_notice = s3_manager.duplication_filtering(crawled_notice)
    if not filtered_notice:
        return "empty"
    else:
        return f'{homepage_title}\n' + make_message(filtered_notice)


for homepage_title, homepage_url in arr.items():
    result = main_logic(homepage_title, homepage_url, manager)
    if result == "empty":
        print(f"{homepage_title} crawling result = no new notice.")
    else:
        message = f"새로운 공지\n" + result + '\n'
        send_telegram(Tokens.YU_TELEGRAM_TOKEN, Tokens.YU_TELEGRAM_CHAT_ID, message)


