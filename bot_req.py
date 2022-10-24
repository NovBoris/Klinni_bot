from bs4 import BeautifulSoup
from requests import get


def check_list():
    url = 'https://cleanny.by/'
    headers = {'user-agent': 'Chrome/89.0.4389.90'}
    r = get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')

    teme = soup.find('div', class_='standartClean')
    res = teme.find('a', class_='button').get('href')
    return res


def cleaners(flag=False):
    url = 'https://cleanny.by/'
    headers = {'user-agent': 'Chrome/89.0.4389.90'}
    r = get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')

    all_cleaners = {}

    teme = soup.find('div', class_='cleaners')
    title = teme.find('h2').get_text(strip=True)
    description = teme.find('div', class_='description').get_text(strip=True)
    teme_cleaners_block = teme.find('div', class_='blocks')
    teme_cleaners = teme_cleaners_block.find_all('div', class_='block')
    for i in teme_cleaners:
        pass
        photo = 'https://cleanny.by' + i.find('img', class_='photo').get('src')
        name = i.find('p', class_='name').get_text(strip=True).split(',')[0]
        all_cleaners[name] = ''
        all_cleaners[name] += i.find('p', class_='name').get_text(strip=True) + '\n'
        all_cleaners[name] += i.find('p', class_='text').get_text(strip=True) + '\n' + photo
    return [title, description, all_cleaners]


def how_work():
    url = 'https://cleanny.by/'
    headers = {'user-agent': 'Chrome/89.0.4389.90'}
    r = get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')

    teme = soup.find('div', class_='howwork')
    res = teme.text.replace('                    ', '').replace('                ', '').replace('\xa0', '') \
        .replace('\r', '').split('\n')
    res = list(filter(lambda x: len(x) > 0, res))
    res[2] += ' ' + res[3]
    del res[3]
    return res


def general_information():
    url = 'https://cleanny.by/'
    headers = {'user-agent': 'Chrome/89.0.4389.90'}
    r = get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')

    teme = soup.find('div', 'importantthing')
    photo = 'https://cleanny.by' + teme.find('img', class_='cemoji').get('src')
    res = teme.text.replace('                    ', '').replace('                ', '').replace('\xa0', '') \
        .replace('\r', '').split('\n')
    res = list(filter(lambda x: len(x) > 0, res))
    return [photo, res]
