import requests
from bs4 import BeautifulSoup as bs
import pymysql
from time import sleep
from plistlib import load
from credential import retrieve
import unicodedata
import json
from datetime import datetime
import os
from pytz import timezone
from logg import *

base = os.path.dirname(os.path.abspath(__file__))+'/'

td = datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S %A")
logger.info('====================')
logger.info(td)
logger.info('====================')

# db credential
cred = load(open(base+'cred.plist','rb'))
user = cred['u']
passwd = cred['p']
dbn = cred['d']

# mastodon credential
instance = 'https://twingyeo.kr'
acc = retrieve('geeknewsbot',instance)
head = {'Authorization':'Bearer '+acc}

#r = bs(requests.get('https://news.hada.io/new').content.decode('utf-8'),'html.parser')
with open(os.path.join(base, 'news.html')) as f:
    r = bs(f.read(), 'html.parser')
table = r.find('article')

pre = []
#item = [f for f in table.find_all('div', class_='votenum')]
all_divs = [x for x in table.find_all('div')]
target_divs = list() # [[topictitle, topicdesc, topicinfo],[topictitle, topicinfo],[]]

# get items sorted
temp_list = list()
for div in all_divs:
    if div['class'][0] == 'topictitle':
        temp_list.append(div)
    if div['class'][0] == 'topicdesc':
        temp_list.append(div)
    if div['class'][0] == 'topicinfo':
        temp_list.append(div)
        target_divs.append(temp_list)
        temp_list = list()

for i in range(len(target_divs)):
    target_divs[i] = bs('\n'.join([str(x) for x in target_divs[i]]), 'html.parser')
    logger.debug(target_divs[i])
    print()

# grab last item
def get_last():
    db = pymysql.connect(host='localhost', user=user, passwd=passwd, db=dbn, charset='utf8')
    try:
        with db.cursor() as cursor:
            q = "select * from geeknews order by id desc limit 1"
            cursor.execute(q)
            r = cursor.fetchall()
            return r
    except:
        logger.error('An unexpected error occurred while getting item')
        return 1
    finally:
        db.close()

# look up id
def look_up_id(nu):
    db = pymysql.connect(host='localhost', user=user, passwd=passwd, db=dbn, charset='utf8')
    try:
        with db.cursor() as cursor:
            q = f"select * from geeknews where id={nu}"
            cursor.execute(q)
            r = cursor.fetchall()[0]
            return 0
    except:
        logger.error('An unexpected error occurred looking up db')
        return 1
    finally:
        db.close()

# add to db

# vid should be int
# vurl, vtitle is required

def add_to(vid, vurl, vtitle, vdesc=''):
    db = pymysql.connect(host='localhost', user=user, passwd=passwd, db=dbn, charset='utf8')
    # check input types
    try:
        if type(vid) is not int:
            logger.debug('id is not int')
            raise ValueError
    except:
        logger.error('input not valid')
        return 1
    vurl = str(vurl)
    vtitle = str(vtitle).replace("'","\\'")
    vdesc = str(vdesc).replace("'","\\'")
    try:
        with db.cursor() as cursor:
            q = f"INSERT INTO geeknews (id, url, title, description) values ('{vid}', '{vurl}', '{vtitle}','{vdesc}')"
            cursor.execute(q)
            db.commit()
            return 0
    except:
        logger.error('An unexpected error occurred while adding to db')
        return 1
    finally:
        db.close()

# func for sending toot message
def send_toot(m):
    da = dict()
    da['status'] = unicodedata.normalize('NFC',m)
    da['visibility'] = 'unlisted'
    r = requests.post(instance+'/api/v1/statuses',headers=head,data=da)
    return r.json()['id']

for t in target_divs:
    topictitle = t.find('div', class_='topictitle').get_text()
    if topictitle.startswith('[flagged]'): # ignore flagged item
        continue
    topicurl = t.find('div', class_='topictitle').a['href']
    try:
        desc = t.find('div', class_='topicdesc').get_text()
    except:
        desc = ''
    #topicid = int(p_bs.find('a',class_='u')['href'].replace('topic?id=',''))
    topicid = int(t.find('a', class_='u')['href'].replace('topic?id=',''))
    if look_up_id(topicid):
        #add_to(topicid, topicurl, topictitle, desc)
        m = topictitle + ' https://news.hada.io/topic?id=' + str(topicid) + '\n' + desc + '\n' + topicurl
        logger.info(m)
        #send_toot(m)
    sleep(1)
