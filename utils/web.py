import csv
import json
import re
from collections import Counter
from datetime import UTC, datetime
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


DEFAULT_COLLECTIONS = (
    {
        "id": "discopolis",
        "title": "Discópolis",
        "subtitle": "Archivo completo exportado desde RTVE Play",
        "source": "files/Discopolis_all.csv",
        "program": "Discópolis",
        "description": (
            "Recorrido cosmopolita por músicas del mundo, rock sinfónico, canción de autor "
            "y sonidos abiertos, presentado por José Miguel López."
        ),
    },
    {
        "id": "discopolis-setentas",
        "title": "Discópolis: Setentas",
        "subtitle": "Serie cronológica sobre la década de los setenta",
        "source": "files/Discopolis_setentas.csv",
        "program": "Discópolis",
        "description": (
            "Serie de Discópolis dedicada a discos, artistas y escenas de los años setenta. "
            "Está pensada para escucharse en orden."
        ),
    },
    {
        "id": "discopolis-sesenta",
        "title": "Discópolis: Los sesenta",
        "subtitle": "Serie monográfica sobre la década de los sesenta y Woodstock",
        "source": "files/Discopolis_sesenta.csv",
        "program": "Discópolis",
        "description": (
            "Serie de Discópolis emitida en 2016 ('Los sesenta de verdad' y especial Woodstock), "
            "ordenada cronológicamente para escuchar en secuencia."
        ),
    },
    {
        "id": "discopolis-1970",
        "title": "Discópolis: 1970",
        "subtitle": "Serie monográfica sobre discos y artistas de 1970",
        "source": "files/Discopolis_1970.csv",
        "program": "Discópolis",
        "description": (
            "Serie de Discópolis dedicada al año 1970, con entregas ordenadas para "
            "seguir el recorrido completo."
        ),
    },
    {
        "id": "discopolis-decada-dorada",
        "title": "Discópolis: Década dorada del Rock",
        "subtitle": "Monográfico en 10 partes sobre el periodo 1966-1975",
        "source": "files/Discopolis_decada_dorada.csv",
        "program": "Discópolis",
        "description": (
            "Monográfico de 10 entregas emitido en julio de 2012 dedicado a la década "
            "dorada del rock (1966-1975)."
        ),
    },
    {
        "id": "discopolis-rock-sinfonico",
        "title": "Discópolis: Rock Sinfónico",
        "subtitle": "Extensa serie dedicada al rock sinfónico y progresivo",
        "source": "files/Discopolis_rock_sinfonico.csv",
        "program": "Discópolis",
        "description": (
            "Serie de más de 150 entregas conducida por José Miguel López repasando "
            "grandes bandas y discos del rock sinfónico y progresivo (Pink Floyd, King Crimson, Yes, etc.)."
        ),
    },
    {
        "id": "6x3",
        "title": "6x3",
        "subtitle": "Archivo completo del programa de Radio 3 dedicado a la guitarra",
        "source": "files/6x3_all.csv",
        "program": "6x3",
        "description": "Programa de Radio 3 dedicado a las seis cuerdas y sus protagonistas.",
    },
    {
        "id": "6x3-rompepistas",
        "title": "6x3: Rompepistas",
        "subtitle": "Selección de sesiones rompepistas del archivo 6x3",
        "source": "files/6x3_rompepistas.csv",
        "program": "6x3",
        "description": "Sesiones rompepistas de 6x3 agrupadas como serie independiente.",
    },
    {
        "id": "musica-y-significado",
        "title": "Música y significado",
        "subtitle": "Archivo completo del programa Música y significado",
        "source": "files/Musica_y_significado_all.csv",
        "program": "Música y significado",
        "description": (
            "Programa de Radio Clásica dedicado a escuchar obras y compositores desde "
            "su contexto musical y cultural."
        ),
    },
    {
        "id": "el-arbol-de-la-musica",
        "title": "El árbol de la música",
        "subtitle": "Archivo completo del programa de Radio Clásica",
        "source": "files/El_arbol_de_la_musica_all.csv",
        "program": "El árbol de la música",
        "description": (
            "Programa de Radio Clásica conducido por Eduardo Martínez-Abarca con "
            "preguntas y reflexiones sobre música e historias fantásticas."
        ),
    },
)

GENERIC_TITLE_WORDS = {
    "discopolis",
    "discópolis",
    "setentas",
    "sesenta",
    "setenta",
    "lista",
    "especial",
    "programa",
    "parte",
    "presenta",
    "presentando",
    "nuevo",
    "nueva",
    "nuevos",
    "talentos",
    "musica",
    "música",
    "canciones",
    "homenaje",
    "entrevista",
    "directo",
    "concierto",
    "the",
    "and",
    "los",
    "las",
    "de",
    "del",
    "la",
    "el",
}


def generar_sitio(output_dir: str = "docs", enrich: bool = False, limit: int | None = None) -> None:
    """Genera una web estática publicable con GitHub Pages."""
    output_path = Path(output_dir)
    data_path = output_path / "data"
    assets_path = output_path / "assets"
    cache_path = Path("files") / "metadata"
    data_path.mkdir(parents=True, exist_ok=True)
    assets_path.mkdir(parents=True, exist_ok=True)
    if enrich:
        cache_path.mkdir(parents=True, exist_ok=True)

    collections = []
    for definition in DEFAULT_COLLECTIONS:
        episodes = load_collection(Path(definition["source"]), definition, limit=limit)
        if enrich:
            for episode in episodes:
                metadata = fetch_episode_metadata(episode, cache_path)
                merge_metadata(episode, metadata)
        collections.append(
            {
                "id": definition["id"],
                "title": definition["title"],
                "subtitle": definition["subtitle"],
                "program": definition["program"],
                "description": definition["description"],
                "source": definition["source"],
                "episodes": episodes,
                "stats": collection_stats(episodes),
            }
        )

    catalog = {
        "generatedAt": datetime.now(UTC).isoformat(timespec="seconds"),
        "enriched": enrich,
        "collections": collections,
    }
    (data_path / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_path / "index.html").write_text(render_index(), encoding="utf-8")
    (assets_path / "styles.css").write_text(render_css(), encoding="utf-8")
    (assets_path / "app.js").write_text(render_js(), encoding="utf-8")
    (output_path / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Sitio generado en {output_path}/index.html")


def load_collection(
    csv_path: Path, definition: dict[str, str], limit: int | None = None
) -> list[dict[str, Any]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"No existe {csv_path}")

    episodes: list[dict[str, Any]] = []
    with csv_path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter=";")
        for index, row in enumerate(reader, start=1):
            if limit is not None and index > limit:
                break
            title = (row.get("Titulo") or "").strip()
            url = normalize_episode_url(row.get("URL") or "")
            asset_id = extract_asset_id(url)
            year = safe_int(row.get("Año"))
            month = safe_int(row.get("Mes"))
            protagonists = extract_protagonists(title)
            episodes.append(
                {
                    "id": f"{definition['id']}-{asset_id or 'row'}-{index}",
                    "assetId": asset_id,
                    "order": index,
                    "episode": row.get("Episodio n") or f"Episodio {index}",
                    "title": title,
                    "program": definition["program"],
                    "collection": definition["id"],
                    "year": year,
                    "month": month,
                    "date": infer_date(title, url, year, month),
                    "url": url,
                    "shareUrl": f"https://rneaudio.rtve.es/a/{asset_id}" if asset_id else url,
                    "audioUrl": f"https://ztnr.rtve.es/ztnr/{asset_id}.mp3" if asset_id else "",
                    "imageUrl": f"https://img.rtve.es/a/{asset_id}/?w=480" if asset_id else "",
                    "duration": "",
                    "description": content_summary(protagonists),
                    "directors": [],
                    "protagonists": protagonists,
                }
            )
    return episodes


def normalize_episode_url(raw_url: str) -> str:
    url = unescape(raw_url.strip())
    matches = re.findall(r"https?://(?:www\.)?rtve\.es/[^\s;]+", url)
    if matches:
        url = matches[-1]
    elif url.startswith("/"):
        url = f"https://www.rtve.es{url}"

    url = url.replace("http://www.rtve.eshttps://www.rtve.es", "https://www.rtve.es")
    url = url.replace("http://www.rtve.eshttp://www.rtve.es", "https://www.rtve.es")
    if url.startswith("http://"):
        url = "https://" + url.removeprefix("http://")
    return url


def extract_asset_id(url: str) -> str:
    parsed = urlparse(url)
    match = re.search(r"/(\d+)/?$", parsed.path)
    return match.group(1) if match else ""


def infer_date(title: str, url: str, year: int | None, month: int | None) -> str:
    haystack = f"{title} {url}"
    match = re.search(r"(?<!\d)(\d{2})[-/](\d{2})[-/](\d{2,4})(?!\d)", haystack)
    if match:
        day, month_text, year_text = match.groups()
        numeric_year = int(year_text)
        if numeric_year < 100:
            numeric_year += 2000 if numeric_year < 70 else 1900
        return f"{numeric_year:04d}-{int(month_text):02d}-{int(day):02d}"
    if year and month:
        return f"{year:04d}-{month:02d}"
    return ""


def safe_int(value: str | None) -> int | None:
    try:
        return int(value) if value not in (None, "") else None
    except ValueError:
        return None


def extract_protagonists(title: str) -> list[str]:
    cleaned = unescape(title)
    cleaned = re.sub(r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b", " ", cleaned)
    cleaned = re.sub(r"^\s*disc[oó]polis\s*\d+\s*[-:]?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"^\s*6\s*x\s*3\s*[-:]?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"^\s*setentas\s*\(?\d+\)?\s*", "", cleaned, flags=re.I)
    cleaned = re.sub(r"^\s*setenta\s*\(?\d+\)?\s*", "", cleaned, flags=re.I)
    cleaned = cleaned.strip(" -–—:.,")

    parts = re.split(r"\s+(?:-|–|—|/|&|\+| y | and )\s+|[,;]", cleaned)
    protagonists: list[str] = []
    seen: set[str] = set()
    for part in parts:
        candidate = re.sub(r"\s+", " ", part).strip(" '‘’\"()[]{}")
        candidate = re.sub(r"\b(?:I{1,3}|IV|V|VI{0,3}|IX|X)\b$", "", candidate).strip()
        if not candidate or len(candidate) < 2:
            continue
        key = candidate.casefold()
        if key in GENERIC_TITLE_WORDS or key.isdigit() or key in seen:
            continue
        if len(candidate.split()) > 7:
            continue
        protagonists.append(candidate)
        seen.add(key)
    return protagonists[:6]

def content_summary(protagonists: list[str]) -> str:
    if not protagonists:
        return "Contenido identificado desde el título original de RTVE."
    return f"Protagonistas identificados: {', '.join(protagonists)}."


def fetch_episode_metadata(episode: dict[str, Any], cache_dir: Path) -> dict[str, Any]:
    asset_id = episode.get("id") or ""
    if not asset_id.isdigit():
        return {}
    cache_file = cache_dir / f"{asset_id}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    response = requests.get(episode["url"], timeout=20)
    response.raise_for_status()
    metadata = parse_episode_metadata(response.text)
    cache_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata


def parse_episode_metadata(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    metadata: dict[str, Any] = {}

    for script in soup.find_all("script", type="application/ld+json"):
        if not script.string:
            continue
        try:
            payload = json.loads(script.string)
        except json.JSONDecodeError:
            continue
        for item in flatten_jsonld(payload):
            if item.get("@type") != "RadioEpisode":
                continue
            audio = item.get("audio") or {}
            if isinstance(audio, list):
                audio = audio[0] if audio else {}
            metadata.update(
                {
                    "description": audio.get("description") or item.get("description") or "",
                    "duration": audio.get("duration") or "",
                    "uploadDate": audio.get("uploadDate") or "",
                    "imageUrl": audio.get("thumbnailUrl") or item.get("image") or "",
                    "directors": people_names(item.get("director")),
                }
            )

    data_file = soup.select_one("[data-file]")
    if data_file and data_file.get("data-file"):
        metadata["audioUrl"] = data_file["data-file"]

    if not metadata.get("description"):
        description = soup.select_one(".mainDescription")
        if description:
            metadata["description"] = " ".join(description.stripped_strings)

    duration = soup.select_one(".duration")
    if duration and not metadata.get("duration"):
        metadata["duration"] = duration.get_text(strip=True)

    return {key: value for key, value in metadata.items() if value}


def flatten_jsonld(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        graph = payload.get("@graph")
        if isinstance(graph, list):
            return [item for item in graph if isinstance(item, dict)]
        return [payload]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def people_names(value: Any) -> list[str]:
    if isinstance(value, dict):
        name = value.get("name")
        return [name] if name else []
    if isinstance(value, list):
        names = []
        for item in value:
            if isinstance(item, dict) and item.get("name"):
                names.append(item["name"])
        return names
    return []


def merge_metadata(episode: dict[str, Any], metadata: dict[str, Any]) -> None:
    for key in ("description", "duration", "uploadDate", "audioUrl", "imageUrl"):
        if metadata.get(key):
            episode[key] = metadata[key]
    if metadata.get("directors"):
        episode["directors"] = metadata["directors"]


def collection_stats(episodes: list[dict[str, Any]]) -> dict[str, Any]:
    protagonist_counter: Counter[str] = Counter()
    years = set()
    for episode in episodes:
        if episode.get("year"):
            years.add(episode["year"])
        protagonist_counter.update(episode.get("protagonists") or [])
    return {
        "episodes": len(episodes),
        "years": sorted(years),
        "topProtagonists": [
            {"name": name, "count": count}
            for name, count in protagonist_counter.most_common(30)
        ],
    }


def render_index() -> str:
    return """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Archivo RNE personal</title>
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
  <header class="hero">
    <p class="eyebrow">RTVE Play / RNE</p>
    <h1>Archivo musical navegable</h1>
    <p>Discópolis, 6x3, Música y significado y sus series publicadas, ordenadas para buscar, filtrar y escuchar en secuencia desde el navegador.</p>
  </header>

  <main class="layout">
    <aside class="panel sidebar">
      <h2>Vistas</h2>
      <nav id="collections" class="collections" aria-label="Colecciones"></nav>
      <section class="stats" id="stats"></section>
    </aside>

    <section class="panel content">
      <div class="toolbar">
        <label>
          Buscar
          <input id="search" type="search" placeholder="artista, título, descripción">
        </label>
        <label class="scope-toggle">
          <input id="globalScope" type="checkbox">
          Buscar en todo el archivo
        </label>
        <label>
          Año
          <select id="yearFilter"></select>
        </label>
        <label>
          Mes
          <select id="monthFilter"></select>
        </label>
        <label>
          Protagonista
          <select id="protagonistFilter"></select>
        </label>
      </div>
      <div id="summary" class="summary"></div>
      <ol id="episodes" class="episodes"></ol>
      <button id="loadMore" class="load-more" type="button">Ver más episodios</button>
    </section>
  </main>

  <footer class="player" aria-live="polite">
    <div class="now-playing">
      <strong id="nowTitle">Selecciona un episodio</strong>
      <span id="nowMeta">El reproductor avanzará al siguiente resultado visible.</span>
    </div>
    <audio id="audio" controls preload="none"></audio>
    <div class="player-actions">
      <button id="previous" type="button">Anterior</button>
      <button id="next" type="button">Siguiente</button>
      <a id="rtveLink" href="https://www.rtve.es/play/radio/" target="_blank" rel="noreferrer">RTVE</a>
    </div>
  </footer>

  <script src="assets/app.js" type="module"></script>
</body>
</html>
"""


def render_css() -> str:
    return """:root {
  color-scheme: dark;
  --bg: #101114;
  --panel: #191b21;
  --panel-2: #20242d;
  --text: #f3f4f6;
  --muted: #aeb4c0;
  --accent: #ffb000;
  --accent-2: #f25f5c;
  --line: #303542;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  min-height: 100vh;
  background: radial-gradient(circle at top left, #342410, transparent 32rem), var(--bg);
  color: var(--text);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  padding-bottom: 8rem;
}

.hero {
  padding: 3rem clamp(1rem, 4vw, 4rem) 2rem;
  max-width: 84rem;
}

.hero h1 {
  font-size: clamp(2rem, 6vw, 5rem);
  line-height: .95;
  margin: .2rem 0 1rem;
}

.hero p { color: var(--muted); max-width: 58rem; }
.eyebrow { color: var(--accent); text-transform: uppercase; letter-spacing: .14em; font-weight: 700; }

.layout {
  display: grid;
  grid-template-columns: minmax(16rem, 22rem) minmax(0, 1fr);
  gap: 1rem;
  padding: 0 clamp(1rem, 4vw, 4rem) 2rem;
}

.panel {
  background: color-mix(in srgb, var(--panel) 92%, transparent);
  border: 1px solid var(--line);
  border-radius: 1.25rem;
  box-shadow: 0 1.5rem 4rem rgb(0 0 0 / .25);
}

.sidebar { align-self: start; padding: 1rem; position: sticky; top: 1rem; }
.content { padding: 1rem; min-width: 0; }

.collections { display: grid; gap: .5rem; }
.collection-button {
  width: 100%;
  text-align: left;
  color: var(--text);
  background: var(--panel-2);
  border: 1px solid var(--line);
  border-radius: .9rem;
  padding: .8rem;
  cursor: pointer;
}
.collection-button[aria-current="true"] { border-color: var(--accent); box-shadow: inset 0 0 0 1px var(--accent); }
.collection-button strong { display: block; }
.collection-button span { color: var(--muted); font-size: .88rem; }

.stats { color: var(--muted); font-size: .92rem; }
.tag-list { display: flex; flex-wrap: wrap; gap: .4rem; margin-top: .75rem; }
.tag {
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--muted);
  padding: .2rem .55rem;
}

.toolbar {
  display: grid;
  grid-template-columns: minmax(14rem, 1fr) repeat(4, minmax(8rem, 12rem));
  gap: .75rem;
  align-items: end;
  margin-bottom: 1rem;
}

label { display: grid; gap: .35rem; color: var(--muted); font-size: .86rem; }
input, select {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: .7rem;
  padding: .65rem .75rem;
  color: var(--text);
  background: #111318;
}
.scope-toggle {
  display: flex;
  align-items: center;
  gap: .55rem;
  align-self: end;
  min-height: 2.8rem;
}
.scope-toggle input { width: auto; }


.summary { color: var(--muted); margin: .5rem 0 1rem; }
.episodes { list-style: none; margin: 0; padding: 0; display: grid; gap: .75rem; }
.episode {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: .85rem;
  background: var(--panel-2);
  border: 1px solid var(--line);
  border-radius: 1rem;
  padding: .85rem;
}
.episode.playing { border-color: var(--accent); }
.episode button {
  inline-size: 3rem;
  block-size: 3rem;
  border-radius: 999px;
  border: 0;
  color: #111;
  background: var(--accent);
  font-weight: 900;
  cursor: pointer;
}
.episode h3 { margin: 0 0 .25rem; font-size: 1.02rem; }
.meta { color: var(--muted); font-size: .88rem; display: flex; flex-wrap: wrap; gap: .7rem; }
.description { color: #d4d7dd; margin: .6rem 0 0; line-height: 1.45; }
.links { display: flex; gap: .75rem; margin-top: .55rem; }
.links a { color: var(--accent); }
.load-more {
  width: 100%;
  margin-top: 1rem;
  border: 1px solid var(--line);
  border-radius: .9rem;
  background: var(--panel-2);
  color: var(--text);
  padding: .85rem;
  cursor: pointer;
}


.player {
  position: fixed;
  inset: auto 0 0;
  display: grid;
  grid-template-columns: minmax(12rem, 1fr) minmax(18rem, 42rem) auto;
  gap: 1rem;
  align-items: center;
  padding: .85rem clamp(1rem, 4vw, 4rem);
  background: rgb(13 14 18 / .94);
  border-top: 1px solid var(--line);
  backdrop-filter: blur(14px);
}
.now-playing { min-width: 0; }
.now-playing strong, .now-playing span { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.now-playing span { color: var(--muted); font-size: .88rem; }
a { color: var(--accent); }
.player-actions { display: flex; gap: .45rem; align-items: center; }
.player-actions button, .player-actions a {
  border: 1px solid var(--line);
  border-radius: .7rem;
  background: var(--panel-2);
  color: var(--text);
  padding: .55rem .7rem;
  text-decoration: none;
}

@media (max-width: 880px) {
  .layout { grid-template-columns: 1fr; }
  .sidebar { position: static; }
  .toolbar { grid-template-columns: 1fr 1fr; }
  .player { grid-template-columns: 1fr; }
}

@media (max-width: 560px) {
  body { padding-bottom: 13rem; }
  .toolbar { grid-template-columns: 1fr; }
  .episode { grid-template-columns: 1fr; }
}
"""


def render_js() -> str:
    return r"""const PAGE_SIZE = 50;

const state = {
  catalog: null,
  collection: null,
  filtered: [],
  currentId: null,
  allEpisodes: [],
  collectionTitles: new Map(),
  visibleLimit: PAGE_SIZE,
};

const els = {
  collections: document.querySelector('#collections'),
  stats: document.querySelector('#stats'),
  search: document.querySelector('#search'),
  year: document.querySelector('#yearFilter'),
  month: document.querySelector('#monthFilter'),
  globalScope: document.querySelector('#globalScope'),
  protagonist: document.querySelector('#protagonistFilter'),
  summary: document.querySelector('#summary'),
  episodes: document.querySelector('#episodes'),
  loadMore: document.querySelector('#loadMore'),
  audio: document.querySelector('#audio'),
  nowTitle: document.querySelector('#nowTitle'),
  nowMeta: document.querySelector('#nowMeta'),
  rtveLink: document.querySelector('#rtveLink'),
  previous: document.querySelector('#previous'),
  next: document.querySelector('#next'),
};

const monthNames = new Intl.DateTimeFormat('es', { month: 'long' });

init();

async function init() {
  const response = await fetch('data/catalog.json');
  state.catalog = await response.json();
  state.collection = state.catalog.collections[0];
  state.allEpisodes = state.catalog.collections.flatMap((collection) => collection.episodes);
  state.collectionTitles = new Map(state.catalog.collections.map((collection) => [collection.id, collection.title]));
  renderCollections();
  renderFilters();
  applyFilters();
  bindEvents();
}

function bindEvents() {
  [els.search, els.year, els.month, els.protagonist].forEach((element) => {
    element.addEventListener('input', applyFilters);
  });
  els.globalScope.addEventListener('change', () => {
    state.currentId = null;
    renderFilters();
    applyFilters();
  });
  els.audio.addEventListener('ended', playNext);
  els.next.addEventListener('click', playNext);
  els.previous.addEventListener('click', playPrevious);
  els.loadMore.addEventListener('click', showMore);
}

function renderCollections() {
  els.collections.innerHTML = '';
  state.catalog.collections.forEach((collection) => {
    const button = document.createElement('button');
    button.className = 'collection-button';
    button.type = 'button';
    button.setAttribute('aria-current', collection.id === state.collection.id ? 'true' : 'false');
    button.innerHTML = `<strong>${escapeHtml(collection.title)}</strong><span>${collection.stats.episodes} episodios</span>`;
    button.addEventListener('click', () => {
      state.collection = collection;
      state.currentId = null;
      state.visibleLimit = PAGE_SIZE;
      els.search.value = '';
      els.globalScope.checked = false;
      renderCollections();
      renderFilters();
      applyFilters();
    });
    els.collections.append(button);
  });
}

function renderFilters() {
  const episodes = activeEpisodes();
  const years = unique(episodes.map((episode) => episode.year).filter(Boolean));
  fillSelect(els.year, 'Todos', years.map((year) => [year, year]));

  const months = unique(episodes.map((episode) => episode.month).filter(Boolean));
  fillSelect(
    els.month,
    'Todos',
    months.map((month) => [month, monthNames.format(new Date(2020, month - 1, 1))])
  );

  const protagonists = unique(episodes.flatMap((episode) => episode.protagonists || []));
  fillSelect(els.protagonist, 'Todos', protagonists.map((name) => [name, name]));

  const stats = isGlobalScope() ? computeStats(episodes) : state.collection.stats;
  const title = isGlobalScope() ? 'Todo el archivo' : state.collection.title;
  const description = isGlobalScope()
    ? `Búsqueda combinada en ${state.catalog.collections.length} colecciones publicadas.`
    : state.collection.description;
  const tags = stats.topProtagonists.slice(0, 12)
    .map((item) => `<span class="tag">${escapeHtml(item.name)} · ${item.count}</span>`)
    .join('');
  els.stats.innerHTML = `
    <h2>${escapeHtml(title)}</h2>
    <p>${escapeHtml(description)}</p>
    <p><strong>${stats.episodes}</strong> episodios · ${years[0] || ''}${years.length > 1 ? `–${years.at(-1)}` : ''}</p>
    <div class="tag-list">${tags}</div>
  `;
}

function applyFilters() {
  const query = normalize(els.search.value);
  const year = els.year.value;
  const month = els.month.value;
  const protagonist = els.protagonist.value;

  state.filtered = activeEpisodes().filter((episode) => {
    const searchable = normalize([
      episode.title,
      episode.description,
      episode.program,
      collectionTitle(episode),
      ...(episode.protagonists || []),
    ].join(' '));
    return (!query || searchable.includes(query))
      && (!year || String(episode.year) === year)
      && (!month || String(episode.month) === month)
      && (!protagonist || (episode.protagonists || []).includes(protagonist));
  });

  state.visibleLimit = PAGE_SIZE;
  renderEpisodes();
}

function renderEpisodes() {
  const fragment = document.createDocumentFragment();
  const visibleEpisodes = state.filtered.slice(0, state.visibleLimit);
  els.episodes.innerHTML = '';
  visibleEpisodes.forEach((episode) => {
    const item = document.createElement('li');
    item.className = `episode${episode.id === state.currentId ? ' playing' : ''}`;
    item.dataset.id = episode.id;
    item.innerHTML = `
      <button type="button" aria-label="Reproducir ${escapeHtml(episode.title)}">▶</button>
      <article>
        <h3>${episode.order}. ${escapeHtml(episode.title)}</h3>
        <div class="meta">
          <span>${escapeHtml(formatDate(episode))}</span>
          ${episode.duration ? `<span>${escapeHtml(formatDuration(episode.duration))}</span>` : ''}
          ${(episode.protagonists || []).length ? `<span>${escapeHtml(episode.protagonists.join(' · '))}</span>` : ''}
          ${isGlobalScope() ? `<span>${escapeHtml(collectionTitle(episode))}</span>` : ''}
        </div>
        ${episode.description ? `<p class="description">${escapeHtml(episode.description)}</p>` : ''}
        <div class="links">
          <a href="${episode.url}" target="_blank" rel="noreferrer">Ficha RTVE</a>
          ${episode.audioUrl ? `<a href="${episode.audioUrl}" target="_blank" rel="noreferrer">MP3</a>` : ''}
        </div>
      </article>
    `;
    item.querySelector('button').addEventListener('click', () => playEpisode(episode));
    fragment.append(item);
  });
  els.episodes.append(fragment);
  els.summary.textContent = `${state.filtered.length} episodios filtrados. Mostrando ${visibleEpisodes.length}. Pulsa ▶ para escuchar y avanzar por el filtro actual.`;
  els.loadMore.hidden = visibleEpisodes.length >= state.filtered.length;
}

function showMore() {
  state.visibleLimit += PAGE_SIZE;
  renderEpisodes();
}

function playEpisode(episode) {
  if (!episode.audioUrl) return;
  state.currentId = episode.id;
  const index = state.filtered.findIndex((item) => item.id === episode.id);
  if (index >= state.visibleLimit) {
    state.visibleLimit = index + 1;
  }
  els.audio.src = episode.audioUrl;
  els.audio.play();
  els.nowTitle.textContent = episode.title;
  els.nowMeta.textContent = `${collectionTitle(episode)} · ${formatDate(episode)}`;
  els.rtveLink.href = episode.url;
  renderEpisodes();
}

function playNext() {
  if (!state.filtered.length) return;
  const index = state.filtered.findIndex((episode) => episode.id === state.currentId);
  playEpisode(state.filtered[index + 1] || state.filtered[0]);
}

function playPrevious() {
  if (!state.filtered.length) return;
  const index = state.filtered.findIndex((episode) => episode.id === state.currentId);
  playEpisode(state.filtered[index - 1] || state.filtered.at(-1));
}


function isGlobalScope() {
  return els.globalScope.checked;
}

function activeEpisodes() {
  return isGlobalScope() ? state.allEpisodes : state.collection.episodes;
}

function collectionTitle(episode) {
  return state.collectionTitles.get(episode.collection) || episode.program || '';
}

function computeStats(episodes) {
  const protagonistCounts = new Map();
  episodes.forEach((episode) => {
    (episode.protagonists || []).forEach((name) => {
      protagonistCounts.set(name, (protagonistCounts.get(name) || 0) + 1);
    });
  });
  return {
    episodes: episodes.length,
    topProtagonists: [...protagonistCounts.entries()]
      .sort(([leftName, leftCount], [rightName, rightCount]) => rightCount - leftCount || leftName.localeCompare(rightName, 'es'))
      .slice(0, 30)
      .map(([name, count]) => ({ name, count })),
  };
}
function fillSelect(select, label, options) {
  select.innerHTML = `<option value="">${label}</option>`;
  options.forEach(([value, text]) => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = text;
    select.append(option);
  });
}

function unique(values) {
  return [...new Set(values)].sort((a, b) => String(a).localeCompare(String(b), 'es', { numeric: true }));
}

function normalize(value) {
  return String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
}

function formatDate(episode) {
  if (episode.date && /^\d{4}-\d{2}-\d{2}$/.test(episode.date)) {
    return new Intl.DateTimeFormat('es', { dateStyle: 'medium' }).format(new Date(`${episode.date}T00:00:00`));
  }
  if (episode.year && episode.month) return `${String(episode.month).padStart(2, '0')}/${episode.year}`;
  return 'Sin fecha';
}

function formatDuration(duration) {
  const match = String(duration).match(/^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$/);
  if (!match) return duration;
  const [, hours = '0', minutes = '0', seconds = '0'] = match;
  return [hours, minutes, seconds]
    .map((part) => String(part).padStart(2, '0'))
    .filter((part, index) => index > 0 || part !== '00')
    .join(':');
}

function escapeHtml(value) {
  return String(value || '').replace(/[&<>'"]/g, (char) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;',
  }[char]));
}
"""
