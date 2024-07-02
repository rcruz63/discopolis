import requests
from bs4 import BeautifulSoup
import csv
import unidecode
import re
import sys


def obtener_all_episodios(literal="all"):
    base_url = "https://www.rtve.es/play/audios/moduloRadio/1936/emisiones"
    episodios = []

    # Convertir el literal a una forma canónica para el nombre del archivo
    literal = literal.strip().lower()
    literal_canonico = re.sub(r'\W+', '_', unidecode.unidecode(literal))

    for year in range(2016, 2021):  # Ajusta los años según sea necesario
        for month in range(12):
            episodios_temp = []
            page_number = 1
            while True:
                url = f"{base_url}?month={month}&year={year}&search=&page={page_number}"
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')

                # Buscar los episodios que contienen el literal en el título
                found = False
                for li in soup.find_all('li', class_='elem_'):
                    title_tag = li.find('span', class_='maintitle')
                    if title_tag:
                        url_tag = li.find('a', class_='goto_media')
                        if url_tag:
                            episodios_temp.append((title_tag.text.strip(), url_tag['href'], year, month+1))
                            found = True

                if not found:
                    break  # No se encontraron más episodios en esta página
                page_number += 1
            episodios_temp.reverse()  # Invertir la lista para que estén en orden cronológico
            episodios.extend(episodios_temp)

    # Crear el archivo CSV
    with open(f'episodios_{literal_canonico}.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Episodio n", "Titulo", "URL", "Año", "Mes"])

        # Recorrer los episodios encontrados
        for i, (titulo, url, year, month) in enumerate(episodios, start=1):
            url_completo = f"http://www.rtve.es{url}"
            writer.writerow([f"Episodio {i}", titulo, url_completo, year, month])

    print(f"Archivo CSV generado con éxito: episodios_{literal_canonico}.csv")

    # Crear el archivo HTML
    with open(f'episodios_{literal_canonico}.html', 'w', newline='', encoding='utf-8-sig') as file:
        file.write('<html>\n<head>\n<title>Lista de Episodios</title>\n</head>\n<body>\n')
        file.write('<h1>Lista de Episodios</h1>\n')
        file.write('<label for="year">Filtrar por año:</label>\n')
        file.write('<select id="year" onchange="filterEpisodes()">\n')
        file.write('<option value="all">Todos</option>\n')
        for year in range(2016, 2021):
            file.write(f'<option value="{year}">{year}</option>\n')
        file.write('</select>\n')
        file.write('<label for="month">Filtrar por mes:</label>\n')
        file.write('<select id="month" onchange="filterEpisodes()">\n')
        file.write('<option value="all">Todos</option>\n')
        for month in range(1, 12):
            file.write(f'<option value="{month}">{month}</option>\n')
        file.write('</select>\n')
        file.write('<ul id="episodeList">\n')
        for i, (titulo, url, year, month) in enumerate(episodios, start=1):
            file.write(f'<li data-year="{year}" data-month="{month}"><a href="{url}">{titulo}</a></li>\n')
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


def obtener_episodios(literal):
    base_url = "https://www.rtve.es/play/audios/moduloRadio/1936/emisiones"
    episodios = []

    # Convertir el literal a una forma canónica para el nombre del archivo
    literal = literal.strip().lower()
    literal_canonico = re.sub(r'\W+', '_', unidecode.unidecode(literal))

    for year in range(2016, 2024):  # Ajusta los años según sea necesario
        for month in range(12):
            episodios_temp = []
            page_number = 1
            while True:
                url = f"{base_url}?month={month}&year={year}&search=&page={page_number}"
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')

                # Buscar los episodios que contienen el literal en el título
                found = False
                for li in soup.find_all('li', class_='elem_'):
                    title_tag = li.find('span', class_='maintitle')
                    if title_tag and literal in title_tag.text.lower():
                        url_tag = li.find('a', class_='goto_media')
                        if url_tag:
                            episodios_temp.append((title_tag.text.strip(), url_tag['href'], year, month+1))
                            found = True

                if not found:
                    break  # No se encontraron más episodios en esta página
                page_number += 1
            episodios_temp.reverse()  # Invertir la lista para que estén en orden cronológico
            episodios.extend(episodios_temp)

    # Crear el archivo CSV
    with open(f'episodios_{literal_canonico}.csv', 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Episodio", "Titulo", "URL", "Año", "Mes"])

        # Recorrer los episodios encontrados
        for i, (titulo, url, year, month) in enumerate(episodios, start=1):
            url_completo = f"http://www.rtve.es{url}"
            writer.writerow([f"Episodio {i}", titulo, url_completo, year, month])

    print(f"Archivo CSV generado con éxito: episodios_{literal_canonico}.csv")

    # Crear el archivo HTML
    with open(f'episodios_{literal_canonico}.html', 'w', newline='', encoding='utf-8') as file:
        file.write('<html>\n<head>\n<title>Lista de Episodios</title>\n</head>\n<body>\n')
        file.write('<h1>Lista de Episodios</h1>\n')
        file.write('<label for="year">Filtrar por año:</label>\n')
        file.write('<select id="year" onchange="filterEpisodes()">\n')
        file.write('<option value="all">Todos</option>\n')
        for year in range(2016, 2024):
            file.write(f'<option value="{year}">{year}</option>\n')
        file.write('</select>\n')
        file.write('<label for="month">Filtrar por mes:</label>\n')
        file.write('<select id="month" onchange="filterEpisodes()">\n')
        file.write('<option value="all">Todos</option>\n')
        for month in range(1, 12):
            file.write(f'<option value="{month}">{month}</option>\n')
        file.write('</select>\n')
        file.write('<ul id="episodeList">\n')
        for i, (titulo, url, year, month) in enumerate(episodios, start=1):
            file.write(f'<li data-year="{year}" data-month="{month}"><a href="{url}">{titulo}</a></li>\n')
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


# Llamada a la función con el literal deseado

if __name__ == "__main__":
    # Se comprueba si hay un argumento
    if len(sys.argv) > 1:
        literal = sys.argv[1]
        obtener_episodios(literal)
    elif len(sys.argv) < 1:
        obtener_all_episodios()
    else:
        sys.exit("Numero de parametros incorrecto")
