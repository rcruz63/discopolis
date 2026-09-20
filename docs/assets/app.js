const PAGE_SIZE = 50;

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
