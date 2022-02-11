from bs4 import BeautifulSoup
from datetime import datetime
import requests
from selenium.webdriver.common.by import By
from selenium import webdriver


def set_driver(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.close()
    return soup


def set_mju_comp_driver(url):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome('chromedriver.exe', options=options)
    driver.get(url)

    # additional action
    driver.switch_to.frame('index_frame')
    driver.find_element(By.XPATH,
                        '//*[@id="pageRightT"]/div[2]/div[1]/div/ul/li[1]/ul/div/div/table/tbody/tr/td/table[1]/tbody/tr/td/a/img').click()

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.close()
    return soup


def crawling_mju_computer_notice(url):
    soup = set_mju_comp_driver(url)
    result = []
    # new articles crawling
    prefix_url = 'http://jw4.mju.ac.kr/user/'
    for tag in soup.select("td > a"):
        for sub_tag in tag.descendants:
            if "img" in str(sub_tag):
                title, link = tag.text.strip(), prefix_url + tag['href']
                result.append([title, link])

    pattern = datetime.today().strftime("%Y-%m")
    i = 0
    for tag in soup.select("td"):
        if pattern in str(tag):
            date = tag.text.strip()
            result[i].append(date)
            i += 1
    return result


def crawling_mju_notice(url):
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


def crawling_yu_notice(url):
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



