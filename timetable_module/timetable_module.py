import requests
import datetime
import urllib.parse
from bs4 import BeautifulSoup

from telegram_bot.config import timetable_endpoint


def get_timetable(groupname):
    url = timetable_endpoint
    groupname_url_encoded = urllib.parse.quote(groupname, safe='')
    current_date = datetime.date.today()
    payload = f"action=showrasp&groupname={groupname_url_encoded}&mydate={current_date.strftime('%d-%m-%Y')}"
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': '_ym_uid=1645160815476899445; BX_USER_ID=23bc072bd3b9acc77df668f2d375fbee; BITRIX_SM_LAST_ADV=5_Y; BITRIX_SM_BANNERS=1_183_4_30122022; BITRIX_SM_GUEST_ID=16022046; BITRIX_SM_LAST_VISIT=03.02.2023+13%3A05%3A24; _ym_d=1679223503; __utmz=253463051.1679223531.25.21.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); PHPSESSID=cnn82hvqh40vfhvcj785jqhtq1; __utma=253463051.1186959541.1647337349.1684840716.1685396763.28; __utmc=253463051; __utmt=1; _ym_isad=2; _ym_visorc=w; __utmb=253463051.8.10.1685396763',
        'Origin': 'https://www.s-vfu.ru',
        'Referer': 'https://www.s-vfu.ru/raspisanie/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    soup = BeautifulSoup(response.text, 'html.parser')

    # Найдем все строки с информацией о занятиях
    rows = soup.find_all('tr')

    lessons_by_day = {}
    lessons_raw = []
    current_weekday = ''

    for row in rows:
        if 'error' in row.get('class', []):
            # Хардкод для обхода
            if row.find_all('th')[0].text.strip() != 'Время':
                current_weekday = row.find_all('th')[0].text.strip()
                lessons_raw = []
        else:
            cells = row.find_all('td')
            time = cells[0].text.strip()
            subject = cells[1].text.strip()
            teacher = cells[2].text.strip()
            classroom = cells[3].text.strip()
            additional_info = cells[4].text.strip()
            lessons_raw.append((time, subject, teacher, classroom, additional_info))
        if current_weekday != '':
            lessons_by_day[current_weekday] = lessons_raw
    return lessons_by_day
