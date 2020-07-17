#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium.webdriver import Chrome, ChromeOptions, Remote
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import time
import re
import sys
import json
import datetime

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.scraping
collection = db.banao1000


# In[2]:


#ユーザー情報
login_ID = '**********'
login_pass = '**********'
chromedriver_pass = 'C:/**********/chromedriver/chromedriver.exe'
line_access_url = 'https://access.line.me/oauth2/v2.1/login?returnUri=%2Foauth2%2Fv2.1%2Fauthorize%2Fconsent%3Fscope%3Dopenid%2Bprofile%2Bfriends%2Bgroups%2Btimeline.post%2Bmessage.write%26response_type%3Dcode%26redirect_uri%3Dhttps%253A%252F%252Ftimeline.line.me%252Fapi%252Fauth%252Fauthorize%253FreturnUrl%253Dhttps%25253A%25252F%25252Ftimeline.line.me%25252Fuser%25252F_dVdyXDuefhwD5dJfZcuyq9iy2XJToflg-P4TZRA%26state%3Da17e520a1752b95c5dec5c6176bdd69f85010e393c91ab3079b31496ea98d42c%26client_id%3D1341209950&loginChannelId=1341209950&loginState=w9vNOgoBgNEXxm75vSiMQE#/'
roop_count = 100


# In[3]:


def main():
    options = ChromeOptions()
    options.add_argument('--headless') # ヘッドレス起動時のみ
    driver = Chrome(executable_path=chromedriver_pass,options=options)
    navigate(driver) # 目標箇所に遷移
    time.sleep(2)
    contents = scrape_contents(driver) # 内容をスクレイピング
    contents = arrange_list(contents) # リストを整理
    print(contents)
    print(len(contents))
    collection.insert_many(contents)


# In[4]:


def navigate(driver):
    driver.get(line_access_url)
    input_element = driver.find_element_by_name('tid')
    input_element.send_keys(login_ID)
    input_element = driver.find_element_by_name('tpasswd')
    input_element.send_keys(login_pass)
    driver.find_element_by_class_name('MdBtn01').click()
    time.sleep(2)
    driver.find_element_by_class_name('MdBtn01').click()
    time.sleep(2)


# In[5]:


def scrape_contents(driver):
    contents = []
    getting_post = 0
    for _ in range(roop_count):
        getting_post += 10
        for article in driver.find_elements_by_css_selector('article.article'):
            if article.text == '':
                continue
            try:
                post_time = article.find_element_by_css_selector('dd.time > a').text
                post_text = article.find_element_by_css_selector('div.article_contents > p.type_text').text
                post_comment = []
                for c in article.find_elements_by_css_selector('dd.comment > p > span'):
                    post_comment.append(c.text)
                post_pic_style = []
                post_pic = []
                for p in article.find_elements_by_css_selector('div.article_contents > div > div > span > a > span[style]'):
                    post_pic_style.append(p)
                for b in post_pic_style:
                    b = b.value_of_css_property('background-image')
                    b = re.findall('"(.*)"',b)
                    b =  ','.join(b)
                    post_pic.append(b)
            except NoSuchElementException:
                post_time = ''
                post_text = ''
                post_comment = ''
                post_pic = ''
            contents.append({
                "time": post_time,
                "text": post_text,
                "comment": post_comment,
                "pic": post_pic,
            })
        try:
            driver.execute_script('scroll(0, document.body.scrollHeight)')
            time.sleep(3) # ここで0.5秒以上待たないと全投稿が読み込めない
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located)
            sys.stdout.write("\r投稿情報取得数：%d" % getting_post)
            sys.stdout.flush()
        except:
            break
    return contents


# In[6]:


"""
# chrome通常起動時
def arrange_list(contents):
    contents = [d for d in contents if d['time'] != '']
    this_year = datetime.date.today().year
    for d in contents:
        if not d['time'].startswith('20'):
            d['time'] = str(this_year) + '. ' + d['time']
    contents = list(map(json.loads, set(map(json.dumps, contents))))
    for l in contents:
        l['time'] = datetime.datetime.strptime(l['time'],'%Y. %m. %d %H:%M')
    contents = sorted(contents, key=lambda s: s['time'])
    return contents
"""


# In[7]:


# chromeヘッドレス起動時
def arrange_list(contents):
    contents = [d for d in contents if d['time'] != '']
    contents = list(map(json.loads, set(map(json.dumps, contents))))
    this_year = datetime.date.today().year
    for d in contents:
        if not d['time'].startswith('20'):
            d['time'] = str(this_year) + '. ' + d['time']
        if d['time'].endswith('am'):
            d['time'] = d['time'][:-3]
            d['time'] = datetime.datetime.strptime(d['time'],'%Y. %m. %d %H:%M')
        if str(d['time']).endswith('pm'):
            d['time'] = d['time'][:-3]
            d['time'] = datetime.datetime.strptime(d['time'],'%Y. %m. %d %H:%M')
            d['time'] = d['time'] + datetime.timedelta(hours=12)
    contents = sorted(contents, key=lambda s: s['time'])
    return contents


# In[8]:


if __name__ == '__main__':
    main()


# In[ ]:





# In[ ]:




