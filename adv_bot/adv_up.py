from gevent import monkey, sleep
import gevent
monkey.patch_all()

import random
import requests
from bs4 import BeautifulSoup


import yaml
import time
import datetime

user_agent = {}
proxies = []
threads = []
BASE_URL = ''
ADV = 'myadvertisements.aspx'
DEFAULT = 'default.aspx'
timeout = 0
timeout_min = 0
timeout_max = 0

logger = None


def sign_in(login, password):
    payload = dict()
    session = requests.session()

    proxy_index = random.randint(0, len(proxies) - 1)
    proxy = proxies[proxy_index]

    r = session.get(BASE_URL + DEFAULT, proxies=proxy)
    soup = BeautifulSoup(r.text)
    form = soup.find('form', attrs={'id': 'form1'})
    inputs = form.findAll('input')

    for i in inputs:
        if i['type'] != 'button':
            payload[i['name']] = i['value']

            if 'UserName' in i['name']:
                payload[i['name']] = login
            else:
                if 'Password' in i['name']:
                    payload[i['name']] = password

    session.post(BASE_URL + DEFAULT, data=payload)
    session.get(BASE_URL + ADV)

    return session


# get all adv-up id from one page
def process_page(page_text):
    soup = BeautifulSoup(page_text)

    adv_ups = soup.findAll('a', attrs={"class": "adv-up"})

    for a in adv_ups:
        yield a['id']


# Get all adv-up ids from all pages
def process_all_pages(start_page, session):
    soup = BeautifulSoup(start_page)

    pages = soup.findAll('div', attrs={"class": "pagins"})
    adv_ups = []

    if len(pages) > 0:
        links = pages[0].findAll('a')
    else:
        for elem in process_page(start_page):
            adv_ups.append(elem)

        return adv_ups

    if len(links) > 0:

        for link in links:
            id = link['id']

            data = {'isPageRequest':True, 'page': id}
            r = session.post(BASE_URL + ADV, data=data)

            for elem in process_page(r.text):
                adv_ups.append(elem)
    else:
        for elem in process_page(start_page):
            adv_ups.append(elem)

    return adv_ups


# Up ll advertisements
def up_all_ads(ads_list, session):
    for adv in ads_list:
        print '   Upping ad with id = ' + adv + " " + str(datetime.datetime.now())
        h = user_agent[random.randint(0, len(user_agent) - 1)]
        session.post(BASE_URL + ADV + '?adv-up=' + adv, headers={"User-Agent": h})


def up_user_ads(login, password):
    session = sign_in(login, password)
    r = session.get(BASE_URL + ADV)

    adv_to_up = process_all_pages(r.text, session)
    up_all_ads(adv_to_up, session)


def worker(cfg):
    global BASE_URL
    global user_agent
    global proxies

    user_agent = cfg['user_agents']
    BASE_URL = cfg['base-url']
    proxies = cfg['proxy']

    global timeout
    global timeout_min
    global timeout_max

    timeout = cfg.get('timeout_base', 300)
    timeout_min = cfg.get('timeout_min', 50)
    timeout_max = cfg.get('timeout_max', 100)

    while True:
        for u in cfg['users']:
            print 'Upping adds for {0} :'.format(u['user_name'])
            up_user_ads(u['user_name'], u['password'])

        sleep(timeout + random.randint(0, 100))


def main():
    with open('config.yaml') as f:
        cfg = yaml.load(f)
        worker(cfg=cfg)


if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            exit(1)
        except Exception:
            import traceback

            traceback.print_exc()
            time.sleep(300)
