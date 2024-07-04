import csv


def escribir_csv(name, episodios, literal_canonico):
    with open(f'files/{name}_{literal_canonico}.csv', 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Episodio n", "Titulo", "URL", "Año", "Mes"])
        for i, (titulo, url, year, month) in enumerate(episodios, start=1):
            url_completo = f"http://www.rtve.es{url}"
            writer.writerow([f"Episodio {i}", titulo, url_completo, year, month])
    print(f"Archivo CSV generado con éxito: {name}_{literal_canonico}.csv")


def escribir_html(name, episodios, literal_canonico, start_year=2016, end_year=2024):
    with open(f'files/{name}_{literal_canonico}.html', 'w', newline='', encoding='utf-8-sig') as file:
        file.write(f'<html>\n<head>\n<title>Lista de Episodios {name} - {literal_canonico}</title>\n</head>\n<body>\n')
        file.write(f'<h1>Lista de Episodios {name} - {literal_canonico}</h1>\n')
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
    print(f"Archivo HTML generado con éxito: Discopolis_{literal_canonico}.html")
