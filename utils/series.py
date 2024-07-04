import pandas as pd
import re
from collections import defaultdict


def load_data(file_path):
    """Cargar datos desde un archivo CSV."""
    return pd.read_csv(file_path, delimiter=';', encoding='utf-8-sig')


def clean_text(text):
    """Limpiar y normalizar texto."""
    text = re.sub(r'[^\w\s]', '', text)  # Eliminar puntuación
    text = text.lower()  # Convertir a minúsculas
    text = text.strip()  # Eliminar espacios en blanco al inicio y final
    return text


def count_words(titles, stop_words, reserved_words):
    """Contar palabras en una lista de títulos, excluyendo stop words y palabras reservadas."""
    word_freq = defaultdict(int)
    for title in titles:
        words = clean_text(title).split()
        for word in words:
            if word not in stop_words and word not in reserved_words and \
               (not word.isdigit() or (word.isdigit() and int(word) > 1900 and int(word) < 2024)):
                word_freq[word] += 1
    return {word: count for word, count in word_freq.items() if count >= 5}


def save_word_frequency(word_freq, output_path):
    """Guardar la frecuencia de palabras en un archivo CSV."""
    df = pd.DataFrame(word_freq.items(), columns=['Palabra', 'Frecuencia'])
    df = df.sort_values(by='Frecuencia', ascending=False)  # Ordenar por frecuencia de mayor a menor
    df.to_csv(output_path, index=False, sep=',', encoding='utf-8-sig')
    return df


def frecuencia(name):
    # Lista de palabras a excluir
    stop_words = set([
        "de", "la", "en", "el", "los", "las", "y", "a", "con",
        "del", "por", "para", "como", "un", "una", "que", "al",
        "se", "su", "le", "les", "lo", "uno", "dos", "tres", "cuatro",
        "cinco", "seis", "siete", "ocho", "nueve", "diez", "cien",
        "mil", "pero", "este", "ese", "aquel", "esos", "esas", "aquellos",
        "aquellas", "mi", "tu", "su", "nuestro", "vuestro", "mis", "tus",
        "sus", "nuestros", "vuestros", "me", "te", "nos", "os", "ellos",
        "ellas", "nosotros", "vosotros", "yo", "tú", "él", "ella",
        "usted", "nosotras", "vosotras", "nosotros", "vosotros",
        "ustedes", "all", "the", "ii", "i", "canción", "music", "música", "iii", "iv",
        "desde", "más", "of", "día"
    ])

    # Lista de palabras reservadas a excluir
    reserved_words = set(["rock", "pop"])

    # Cargar datos
    file_path = f'./{name}_all.csv'
    df = load_data(file_path)

    # Contar palabras en títulos
    word_freq = count_words(df['Titulo'], stop_words, reserved_words)

    # Guardar resultado en un archivo CSV
    output_path = f'./files/frecuencia_palabras_{name}.csv'
    df_sorted = save_word_frequency(word_freq, output_path)

    print(f"Análisis completado y guardado en 'frecuencia_palabras_{name}.csv'")

    # Mostrar el resultado
    # for word, freq in df_sorted.iterrows():
    #    print(f"{word}: {freq}")

    for _, row in df_sorted.iterrows():
        print(f"{row['Palabra']}: {row['Frecuencia']}")
