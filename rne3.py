import sys

from utils.episodios import episodios
from utils.series import frecuencia

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
    }
}

if __name__ == "__main__":
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
        print("Programas disponibles:")
        for clave, programa in constantes_programas.items():
            print(f"Clave: {clave}, Nombre: {programa['name']}")

    else:
        sys.exit("Número incorrecto de parámetros")
