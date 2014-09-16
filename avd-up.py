import logging
import random
import requests
from BeautifulSoup import BeautifulSoup

from gevent import monkey; monkey.patch_all()

import gevent
import yaml
import time
import logging.config

user_agent = {}
BASE_URL = ''
timeout = 300

logger = None


def set_logger(log):
    global logger
    logger = log


def setup_logger(config):
    with open(config['log_settings']) as f:
        cfg = yaml.load(f)
        logging.config.dictConfig(cfg)
        set_logger(logging.getLogger('clogger'))



def sign_in(login, password):

    payload = dict()
    # payload['HomeLeft__339$Login__265$tbUserName'] = login
    # payload['HomeLeft__339$Login__265$tbPassword'] = passowrd

    session = requests.session()
    r = session.get('http://premier.ua/default.aspx')
    soup = BeautifulSoup(r.text)
    form = soup.find('form',attrs={'id':'form1'})
    inputs = form.findAll('input')

    for i in inputs:
        if i['type'] != 'button':
            payload[i['name']] = i['value']

            if 'UserName' in i['name']:
                payload[i['name']] = login
            else:
                if 'Password' in i['name']:
                    payload[i['name']] = password



    r = session.post('http://premier.ua/default.aspx', data=payload)
    r = session.get(BASE_URL)

    print r.text

    r = requests.get(BASE_URL)
    r = requests.post('http://premier.ua/myadvertisements.aspx', data=payload, files={'':''})
    cookies = r.cookies

    cookies['ASP.NET_SessionId'] = 'cbxa5t3jvhynw055ffmvdm45'
    r = requests.get(BASE_URL, cookies=cookies)

    return cookies


#get all adv-up id from one page
def process_page(page_text):
    soup = BeautifulSoup(page_text)

    adv_ups = soup.findAll('a', attrs={"class": "adv-up"})

    for a in adv_ups:
        yield a['id']


#Get all adv-up ids from all pages
def process_all_pages(start_page, cookies):
    soup = BeautifulSoup(start_page)

    pages = soup.findAll('div', attrs={"class":"pagins"})
    adv_ups = []

    if len(pages) > 0:
        links = pages[0].findAll('a')

    if len(links) > 0:

        for link in links:
            id = link['id']

            data = {'isPageRequest':True, 'page' : id}
            r = requests.post(BASE_URL, data=data, cookies=cookies)

            for elem in process_page(r.text):
                adv_ups.append(elem)
    else:
        for elem in process_page(start_page):
            adv_ups.append(elem)

    return adv_ups


#Up ll advertisements
def up_all_ads(ads_list, cookies):
    for adv in ads_list:
        logger.info('       Upping ad with id = ' +  adv)
        h = user_agent[random.randint(0, len(user_agent) - 1)]
        requests.post(BASE_URL + '?adv-up=' + adv, cookies=cookies, headers={"User-Agent" : h})


def up_user_ads(login, password):
    c = sign_in(login, password)
    r = requests.get(BASE_URL, cookies=c)

    adv_to_up = process_all_pages(r.text, c)
    up_all_ads(adv_to_up, c)


def worker(login, password):
    while True:
        logger.info('Upping ads for user ' + login)
        up_user_ads(login, password)
        time.sleep(timeout + random.randint(100, 600))


if __name__ == '__main__':
    with open('config.yaml') as f:
        cfg = yaml.load(f)
        setup_logger(cfg)
        user_agent = cfg['user_agents']
        BASE_URL = cfg['base-url']


        list = []
        for u in cfg['users']:
                gevent.spawn(worker(u['user_name'], u['password']))


