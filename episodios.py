import requests
from bs4 import BeautifulSoup
import csv
import unidecode
import re
import sys


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


def obtener_episodios(literal, start_year=2016, end_year=2024):
    base_url = "https://www.rtve.es/play/audios/moduloRadio/1936/emisiones"
    episodios = []
    literal_canonico = re.sub(r'\W+', '_', unidecode.unidecode(literal.strip().lower()))

    for year in range(start_year, end_year):
        for month in range(12):
            episodios.extend(obtener_episodios_por_mes(base_url, year, month, literal))
    return episodios, literal_canonico


def obtener_all_episodios(start_year=2016, end_year=2024):
    base_url = "https://www.rtve.es/play/audios/moduloRadio/1936/emisiones"
    episodios = []
    literal_canonico = "all"

    for year in range(start_year, end_year):
        for month in range(12):
            episodios.extend(obtener_episodios_por_mes(base_url, year, month))
    return episodios, literal_canonico


def escribir_csv(episodios, literal_canonico):
    with open(f'episodios_{literal_canonico}.csv', 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Episodio n", "Titulo", "URL", "Año", "Mes"])
        for i, (titulo, url, year, month) in enumerate(episodios, start=1):
            url_completo = f"http://www.rtve.es{url}"
            writer.writerow([f"Episodio {i}", titulo, url_completo, year, month])
    print(f"Archivo CSV generado con éxito: episodios_{literal_canonico}.csv")


def escribir_html(episodios, literal_canonico, start_year=2016, end_year=2024):
    with open(f'episodios_{literal_canonico}.html', 'w', newline='', encoding='utf-8-sig') as file:
        file.write('<html>\n<head>\n<title>Lista de Episodios</title>\n</head>\n<body>\n')
        file.write('<h1>Lista de Episodios</h1>\n')
        file.write('<label for="year">Filtrar por año:</label>\n')
        file.write('<select id="year" onchange="filterEpisodes()">\n')
        file.write('<option value="all">Todos</option>\n')
        for year in range(start_year, end_year):
            file.write(f'<option value="{year}">{year}</option>\n')
        file.write('</select>\n')
        file.write('<label for="month">Filtrar por mes:</label>\n')
        file.write('<select id="month" onchange="filterEpisodes()">\n')
        file.write('<option value="all">Todos</option>\n')
        for month in range(1, 13):
            file.write(f'<option value="{month}">{month}</option>\n')
        file.write('</select>\n')
        file.write('<ul id="episodeList">\n')
        for i, (titulo, url, year, month) in enumerate(episodios, start=1):
            url_completo = f"http://www.rtve.es{url}"
            file.write(f'<li data-year="{year}" data-month="{month}"><a href="{url_completo}">{titulo}</a></li>\n')
        file.write('</ul>\n')
        file.write('''
<script>
function filterEpisodes() {
    var year = document.getElementById('year').value;
    var month = document.getElementById('month').value;
    var episodes = document.getElementById('episodeList').getElementsByTagName('li');
    for (var i = 0; i < episodes.length; i++) {
        var episodeYear = episodes[i].getAttribute('data-year');
        var episodeMonth = episodes[i].getAttribute('data-month');
        if ((year === 'all' || episodeYear === year) && (month === 'all' || episodeMonth === month)) {
            episodes[i].style.display = '';
        } else {
            episodes[i].style.display = 'none';
        }
    }
}
</script>
''')
        file.write('</body>\n</html>')
    print(f"Archivo HTML generado con éxito: episodios_{literal_canonico}.html")


def main(literal=None):
    if literal:
        episodios, literal_canonico = obtener_episodios(literal)
    else:
        episodios, literal_canonico = obtener_all_episodios()
    escribir_csv(episodios, literal_canonico)
    escribir_html(episodios, literal_canonico)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        literal = sys.argv[1]
        main(literal)
    elif len(sys.argv) == 1:
        main()
    else:
        sys.exit("Numero incorrecto de parametros")
