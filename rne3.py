import sys

from utils.episodios import episodios
from utils.series import frecuencia
from utils.web import generar_sitio

# Definición de constantes para cada programa
constantes_programas = {
    "discopolis": {
        "name": "Discopolis",
        "base_url": "https://www.rtve.es/play/audios/moduloRadio/1936/emisiones",
        "month": 5,
        "year": 2008
    },
    "6x3": {
        "name": "6x3",
        "base_url": "https://www.rtve.es/play/audios/moduloRadio/58211/emisiones",
        "month": 9,
        "year": 2012
    },
    "significado": {
        "name": "Musica_y_significado",
        "base_url": "https://www.rtve.es/play/audios/moduloRadio/40382/emisiones",
        "month": 3,
        "year": 2010
    },
    "arbol": {
        "name": "El_arbol_de_la_musica",
        "base_url": "https://www.rtve.es/play/audios/moduloRadio/119930/emisiones",
        "month": 10,
        "year": 2018
    }
}

def generar_web(args):
    enrich = "--enrich" in args
    limit = None
    for index, arg in enumerate(args):
        if arg == "--limit" and index + 1 < len(args):
            limit = int(args[index + 1])
    generar_sitio(enrich=enrich, limit=limit)


def mostrar_programas():
    print("Programas disponibles:")
    for clave, programa in constantes_programas.items():
        print(f"Clave: {clave}, Nombre: {programa['name']}")
    print("Clave: site, Nombre: Web estática GitHub Pages")


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1].lower() in {"site", "web", "pages"}:
        generar_web(sys.argv[2:])
        sys.exit(0)

    if len(sys.argv) == 3:
        programa = sys.argv[1]
        if programa.lower() in constantes_programas:
            constantes = constantes_programas[programa]
            literal = sys.argv[2]
            episodios(constantes, literal)
        else:
            sys.exit("Programa no reconocido")
    elif len(sys.argv) == 2:
        programa = sys.argv[1]
        if programa.lower() in constantes_programas:
            constantes = constantes_programas[programa]
            episodios(constantes)
            # print("Frecuencia")
            frecuencia(constantes["name"])
        else:
            sys.exit("Programa no reconocido")
    elif len(sys.argv) == 1:
        mostrar_programas()

    else:
        sys.exit("Número incorrecto de parámetros")
