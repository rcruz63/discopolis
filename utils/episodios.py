import requests
from bs4 import BeautifulSoup
import unidecode
import re

from utils.escribir import escribir_csv, escribir_html


def obtener_episodios_por_mes(base_url, year, month, literal=None):
    # print(year, " - ", month, " - pag 1")
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
        # print(year, " - ", month, " - pag ", page_number)
    episodios_temp.reverse()
    return episodios_temp


def obtener_episodios(programa, literal, start_year=None, end_year=2024):
    base_url = programa["base_url"]
    episodios = []
    if not start_year:
        start_year = programa["year"]
        for month in range((programa["month"] - 1), 12):
            episodios.extend(obtener_episodios_por_mes(base_url, start_year, month, literal))
        start_year += 1

    literal_canonico = re.sub(r'\W+', '_', unidecode.unidecode(literal.strip().lower()))

    for year in range(start_year, end_year):
        for month in range(12):
            episodios.extend(obtener_episodios_por_mes(base_url, year, month, literal))
    return episodios, literal_canonico


def obtener_all_episodios(programa, start_year=None, end_year=2024):
    base_url = programa["base_url"]
    episodios = []
    if not start_year:
        start_year = programa["year"]
        for month in range((programa["month"] - 1), 12):
            episodios.extend(obtener_episodios_por_mes(base_url, start_year, month))
        start_year += 1
    literal_canonico = "all"

    for year in range(start_year, end_year):
        print("Year:", year)
        for month in range(12):
            episodios.extend(obtener_episodios_por_mes(base_url, year, month))
    return episodios, literal_canonico


def episodios(programa, literal=None):
    if literal:
        episodios, literal_canonico = obtener_episodios(programa, literal)
    else:
        episodios, literal_canonico = obtener_all_episodios(programa)
    print("Ha escribir CSV")
    escribir_csv(programa["name"], episodios, literal_canonico)
    print("Ha escribir HTML")
    escribir_html(programa["name"], episodios, literal_canonico)
