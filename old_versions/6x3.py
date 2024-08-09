import sys

from utils.episodios import episodios
from utils.series import frecuencia


name = '6x3'
base_url = "https://www.rtve.es/play/audios/moduloRadio/58211/emisiones"

if __name__ == "__main__":
    if len(sys.argv) == 2:
        literal = sys.argv[1]
        episodios(name, base_url, literal)
    elif len(sys.argv) == 1:
        episodios(name, base_url)
        frecuencia(name)
    else:
        sys.exit("Numero incorrecto de parametros")
