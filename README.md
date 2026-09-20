# discopolis

Archivo personal de emisiones musicales de RNE/RTVE Play. Genera listados CSV/HTML y una web estática publicable en GitHub Pages para buscar, filtrar y escuchar episodios desde el navegador.

## Uso

```bash
# Listar programas disponibles
python rne3.py

# Regenerar los CSV/HTML originales
python rne3.py discopolis
python rne3.py discopolis setentas
python rne3.py 6x3

# Generar la web estática en docs/
python rne3.py site

# Opcional: enriquecer episodios consultando cada ficha de RTVE
python rne3.py site --enrich
```

## Web GitHub Pages

El comando `python rne3.py site` crea:

- `docs/index.html`
- `docs/assets/app.js`
- `docs/assets/styles.css`
- `docs/data/catalog.json`

Configura GitHub Pages para publicar desde la carpeta `docs/`. La web incluye las vistas `Discópolis`, `Discópolis: Setentas` y `6x3`, filtros por texto/año/mes/protagonista, enlace a la ficha de RTVE y reproducción directa mediante los MP3 públicos de RTVE (`https://ztnr.rtve.es/ztnr/{id}.mp3`).

La identificación de protagonistas se infiere desde los títulos. Con `--enrich` también se incorporan descripciones, duración y dirección cuando la ficha pública de RTVE las expone.
