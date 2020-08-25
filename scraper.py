#!/usr/bin/env python3
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests

group_name = 11852


def get_timetable(group_id, date):
    page = requests.post(f"http://www.osu.ru/pages/schedule/?who=1&what=1&filial=1&group={group_id}&mode=full")
    bsObj = BeautifulSoup(page.text, features='html.parser')
    for tag in bsObj.find_all('tr', {'style': True}):
        if date == tag.contents[0].next:
            pare_id = [int(nam.attrs['pare_id']) for nam in tag.find_all('td', {'pare_id': True})]
            disciplines = [val.attrs['title'] for val in tag.find_all('span', {'class': 'dis'})]
            auditorium = [aud.text for aud in tag.find_all('span', {'class': 'aud'})]
            teacher = [teach.text for teach in tag.find_all('span', {'class': 'p'})]
            day = ''
            k = 0
            for i in pare_id:
                day += f"{i} - {disciplines[k]}\n\tАудитория - {auditorium[k]}\n\tПреподаватель - {teacher[k]}\n"
                k += 1
            if len(day) != 0:
                return day
            else:
                return 'В данный день пар нет'


class Scraper:
    def __init__(self):
        self.faculty_request = "http://www.osu.ru/pages/schedule/?who=1"
        self.for_requests = "http://www.osu.ru/pages/schedule/index.php"

    def get_faculty(self):
        html = urlopen(self.faculty_request)
        bsObj = BeautifulSoup(html, features="html.parser")
        div_pars = bsObj.find_all('option', {'value': True, 'title': True})
        values = {}
        values_swapped = {}
        for tag in div_pars:
            values.setdefault(tag.text, int(tag.attrs['value']))
            values_swapped.setdefault(str(tag.attrs['value']), tag.text)
        return values, values_swapped

    def get_courses(self, faculty_id):
        to_send = {
            'who': 1,
            'what': 1,
            'request': 'potok',  # group для группы, potok для курса
            'filial': 1,
            'mode': 'full',
            'facult': faculty_id
        }
        page = requests.post(self.for_requests, data=to_send)
        bsObj = BeautifulSoup(page.text, features="html.parser")
        values = bsObj.find_all('option', {'value': True, 'onclick': True, 'title': False})
        data = {}
        data_swapped = {}
        for value in values:
            data.setdefault(value.text, int(value.attrs['value']))
            data_swapped.setdefault(value.attrs['value'], value.text)
        return data, data_swapped

    def get_groups(self, faculty_id, course_id):
        to_send = {
            'who': 1,
            'what': 1,
            'request': 'group',
            'filial': 1,
            'mode': 'full',
            'facult': faculty_id,
            'potok': course_id
        }
        page = requests.post(self.for_requests, data=to_send)
        bsObj = BeautifulSoup(page.text, features='html.parser')
        values = bsObj.find_all('option', {'value': True, 'onclick': True, 'title': False})
        data = {}
        data_swapped = {}
        for value in values:
            if 'rasp' in value.attrs['onclick']:
                data.setdefault(value.text, int(value.attrs['value']))
                data_swapped.setdefault(value.attrs['value'], value.text)
        return data, data_swapped


def scrape(group_id):
    page = urlopen(f"http://www.osu.ru/pages/schedule/?who=1&what=1&filial=1&group={group_id}&mode=full")
    html = page.read()
    parser = "html.parser"
    sp = BeautifulSoup(html, parser)
    date_input = '09.12.2020'
    k = 0
    list = []
    pars = sp.find_all('tr', {'style': True})
    for tag in sp.find_all('tr', {'style': True}):
        date = tag.contents[0].next
        if date == date_input:
            pare_id = [int(nam.attrs['pare_id']) for nam in tag.find_all('td', {'pare_id': True})]
            disciplines = [val.attrs['title'] for val in tag.find_all('span', {'class': 'dis'})]
            auditorium = [aud.text for aud in tag.find_all('span', {'class': 'aud'})]
            teacher = [teach.text for teach in tag.find_all('span', {'class': 'p'})]
            day = ''
            k = 0
            for i in pare_id:
                day += f"{i} - {disciplines[k]}\nАудитория - {auditorium[k]}\nПреподаватель - {teacher[k]}\n"
                k += 1
            print(day)
            break
