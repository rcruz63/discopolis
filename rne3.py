import sys

from utils.episodios import episodios
from utils.series import frecuencia

# Definición de constantes para cada programa
constantes_programas = {
    "discopolis": {
        "name": "Discopolis",
        "base_url": "https://www.rtve.es/play/audios/moduloRadio/1936/emisiones",
    },
    "6x3": {
        "name": "6x3",
        "base_url": "https://www.rtve.es/play/audios/6x3/emisiones",
    }
}

if __name__ == "__main__":
    if len(sys.argv) == 3:
        programa = sys.argv[1]
        if programa in constantes_programas:
            constantes = constantes_programas[programa]
            literal = sys.argv[2]
            episodios(constantes["name"], constantes["base_url"], literal)
        else:
            sys.exit("Programa no reconocido")
    elif len(sys.argv) == 2:
        programa = sys.argv[1]
        if programa in constantes_programas:
            constantes = constantes_programas[programa]
            episodios(constantes["name"], constantes["base_url"])
            frecuencia(constantes["name"])
        else:
            sys.exit("Programa no reconocido")
    else:
        sys.exit("Número incorrecto de parámetros")