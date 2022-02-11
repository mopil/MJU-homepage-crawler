import telegram
import requests


def make_message(result):
    message = ""
    for notice in result:
        message += str(notice[0]) + '\n' + str(notice[1]) + '\n\n'
    return message


def send_telegram(token, chat_id, message):
    my_bot = telegram.Bot(token)
    my_bot.sendMessage(chat_id=chat_id, text=message)


def send_slack(token, chat_id, message):
    post_url = "https://slack.com/api/chat.postMessage"
    header = {"Authorization": "Bearer " + token}
    data = {"channel": chat_id, "text": message}
    requests.post(post_url, headers=header, data=data)