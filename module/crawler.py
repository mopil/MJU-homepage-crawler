from bs4 import BeautifulSoup
import requests
from selenium.webdriver.common.by import By
from selenium import webdriver
import message_manager


def crawling_mju_computer_notice(url):
    # selenium driver setting
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.get(url)
    driver.switch_to.frame('index_frame')
    driver.find_element(By.XPATH,
                        '//*[@id="pageRightT"]/div[2]/div[1]/div/ul/li[1]/ul/div/div/table/tbody/tr/td/table[1]/tbody/tr/td/a/img').click()
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    result = []
    prefix_url = 'http://jw4.mju.ac.kr/user/'
    for tag in soup.select("td > a"):
        for sub_tag in tag.descendants:
            if "img" in str(sub_tag):
                title, link = tag.text.strip(), prefix_url + tag['href']
                result.append([title, link])
    return result


def crawling_mju_common_notice(url):
    prefix_url = 'http://www.mju.ac.kr'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    result = []
    for tag in soup.select('.artclLinkView'):
        title, link = tag.text, prefix_url + tag['href']
        if "새글" in title:
            result.append([title.replace("새글", "").strip(), link])
    return result


def crawling_yu_common_notice(url):
    prefix_url = url
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, 'html.parser')
    result = []
    for tag in soup.select('.b-title-box > a'):
        title, link = tag['title'], prefix_url + tag['href']
        if 'comment' not in link:
            result.append([title, link])
    return result


def main_logic(homepage_title, homepage_url, crawling_method, s3_manager):
    crawled_notice = crawling_method(homepage_url)
    filtered_notice = s3_manager.duplication_filtering(crawled_notice)
    if not filtered_notice:
        return "empty"
    else:
        return f'{homepage_title}\n' + message_manager.make_message(filtered_notice)
