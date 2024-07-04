import requests
from bs4 import BeautifulSoup
import unidecode
import re

from utils.escribir import escribir_csv, escribir_html


def obtener_episodios_por_mes(base_url, year, month, literal=None):
    episodios_temp = []
    page_number = 1
    while True:
        url = f"{base_url}?month={month}&year={year}&search=&page={page_number}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        found = False
        for li in soup.find_all('li', class_='elem_'):
            title_tag = li.find('span', class_='maintitle')
            if title_tag and (literal is None or literal in title_tag.text.lower()):
                url_tag = li.find('a', class_='goto_media')
                if url_tag:
                    episodios_temp.append((title_tag.text.strip(), url_tag['href'], year, month + 1))
                    found = True
        if not found:
            break
        page_number += 1
    episodios_temp.reverse()
    return episodios_temp


def obtener_episodios(base_url, literal, start_year=2012, end_year=2024):
    episodios = []
    literal_canonico = re.sub(r'\W+', '_', unidecode.unidecode(literal.strip().lower()))

    for year in range(start_year, end_year):
        for month in range(12):
            episodios.extend(obtener_episodios_por_mes(base_url, year, month, literal))
    return episodios, literal_canonico


def obtener_all_episodios(base_url, start_year=2012, end_year=2024):
    episodios = []
    literal_canonico = "all"

    for year in range(start_year, end_year):
        for month in range(12):
            episodios.extend(obtener_episodios_por_mes(base_url, year, month))
    return episodios, literal_canonico


def episodios(name, base_url, literal=None):
    if literal:
        episodios, literal_canonico = obtener_episodios(base_url, literal)
    else:
        episodios, literal_canonico = obtener_all_episodios(base_url)
    escribir_csv(name, episodios, literal_canonico)
    escribir_html(name, episodios, literal_canonico)
