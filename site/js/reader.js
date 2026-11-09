/**
 * Reading Greek — Interactive Reader & Word Card Module
 */

import { openProofread } from './proofread.js';

let currentTextData = null;
let currentVocabData = [];
let currentGuideData = null;
let activePassageId = null;
let lsjCache = null;

async function loadLSJCache() {
  if (lsjCache) return lsjCache;
  try {
    const prefix = window.location.pathname.includes('/site') ? '../' : './';
    let r = await fetch(prefix + 'data/vocab/lsj_cache.json');
    if (!r.ok) r = await fetch('../data/vocab/lsj_cache.json');
    if (!r.ok) r = await fetch('./data/vocab/lsj_cache.json');
    if (!r.ok) r = await fetch('./site/data/lsj_cache.json');
    if (r.ok) {
      lsjCache = await r.json();
    }
  } catch (e) {
    console.warn('Could not load local LSJ cache:', e);
  }
  return lsjCache || {};
}

async function queryLSJ(tokenText, lemmaText) {
  const contentEl = document.getElementById('card-lsj-content');
  const logeionLink = document.getElementById('card-logeion-link');
  const perseusLink = document.getElementById('card-perseus-link');
  const lemmaSpan = document.getElementById('card-lemma');
  const glossSpan = document.getElementById('card-gloss');

  if (!contentEl) return;

  const cleanWord = tokenText.replace(/[.,;·'’"()[\]]/g, '').trim();
  const searchKey = lemmaText ? lemmaText.replace(/[.,;·'’"()[\]]/g, '').trim() : cleanWord;

  if (logeionLink) logeionLink.href = `https://logeion.uchicago.edu/${encodeURIComponent(searchKey)}`;
  if (perseusLink) perseusLink.href = `https://www.perseus.tufts.edu/hopper/morph?l=${encodeURIComponent(cleanWord)}&la=greek`;

  contentEl.innerHTML = '<p class="lsj-loading text-muted">🔍 Searching LSJ lexicon...</p>';

  const cache = await loadLSJCache();
  const entry = cache[cleanWord] || (lemmaText && cache[lemmaText]) || cache[cleanWord.replace(/-/g, '')];

  if (entry && entry.html) {
    contentEl.innerHTML = `
      <div class="lsj-entry-body">
        <div style="margin-bottom:0.4rem;"><strong>Headword:</strong> <span style="font-family:var(--font-greek); color:var(--terracotta); font-size:1.15rem; font-weight:700;">${entry.headword}</span></div>
        <div class="lsj-full-text">${entry.html}</div>
      </div>
    `;
    if (lemmaSpan && (lemmaSpan.textContent === '—' || lemmaSpan.textContent === 'Looking up...')) {
      lemmaSpan.textContent = entry.headword;
    }
    if (glossSpan && glossSpan.textContent.includes('LSJ')) {
      glossSpan.textContent = entry.short_def || entry.headword;
    }
    return;
  }

  // Fallback to online Wiktionary Ancient Greek API
  try {
    const onlineUrl = `https://en.wiktionary.org/api/rest_v1/page/definition/${encodeURIComponent(cleanWord)}`;
    const resp = await fetch(onlineUrl);
    if (resp.ok) {
      const data = await resp.json();
      const greekItems = (data.other || []).filter(item => item.language === 'Ancient Greek');
      if (greekItems.length) {
        let outHtml = `<div><strong>Ancient Greek Wiktionary:</strong></div>`;
        greekItems.forEach(item => {
          outHtml += `<div style="margin-top:0.4rem;"><span class="badge" style="background:rgba(47,93,124,0.12); color:var(--aegean); font-size:0.75rem; padding:0.15rem 0.4rem; border-radius:3px;">${item.partOfSpeech || 'Ancient Greek'}</span></div>`;
          outHtml += `<ul style="padding-left:1.2rem; margin:0.3rem 0;">`;
          (item.definitions || []).forEach(d => {
            outHtml += `<li>${d.definition}</li>`;
          });
          outHtml += `</ul>`;
        });
        contentEl.innerHTML = outHtml;
        if (glossSpan && glossSpan.textContent.includes('LSJ') && greekItems[0].definitions && greekItems[0].definitions[0]) {
          const tempDiv = document.createElement('div');
          tempDiv.innerHTML = greekItems[0].definitions[0].definition;
          glossSpan.textContent = tempDiv.textContent.slice(0, 150);
        }
        return;
      }
    }
  } catch (err) {
    console.log('Online lookup error:', err);
  }

  contentEl.innerHTML = `
    <p class="text-muted">No entry found in local cache. You can view the full entry online:</p>
    <div style="display:flex; gap:0.5rem; margin-top:0.5rem;">
      <a href="${logeionLink ? logeionLink.href : '#'}" target="_blank" class="card-action-btn" style="flex:1;">Open in Logeion ↗</a>
    </div>
  `;
}

export function initReader(textData, vocabData, guideData) {
  currentTextData = textData;
  currentVocabData = vocabData;
  currentGuideData = guideData;

  const btnGroup = document.getElementById('passage-btn-group');
  btnGroup.innerHTML = '';

  if (!textData || !textData.passages || !textData.passages.length) {
    document.getElementById('passage-lines-container').innerHTML = '<p>No passage data loaded for this section.</p>';
    return;
  }

  textData.passages.forEach((p, idx) => {
    const btn = document.createElement('button');
    btn.className = `passage-btn ${idx === 0 ? 'active' : ''}`;
    btn.textContent = p.id;
    btn.addEventListener('click', () => {
      document.querySelectorAll('.passage-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      loadPassage(p.id);
    });
    btnGroup.appendChild(btn);
  });

  initToggles();
  initDrawerEvents();

  // Load first passage
  loadPassage(textData.passages[0].id);
}

export function loadPassage(passageId) {
  activePassageId = passageId;
  const passage = currentTextData.passages.find(p => p.id === passageId);
  if (!passage) return;

  document.getElementById('passage-title').textContent = passage.title || `Passage ${passage.id}`;
  document.getElementById('passage-intro').textContent = passage.intro_en || '';

  const linesContainer = document.getElementById('passage-lines-container');
  linesContainer.innerHTML = '';

  passage.lines.forEach(line => {
    if (line.direction && !line.greek) {
      // Standalone stage direction
      const dirRow = document.createElement('div');
      dirRow.className = 'stage-direction-row';
      dirRow.textContent = line.direction.text;
      linesContainer.appendChild(dirRow);
      return;
    }

    const lineRow = document.createElement('div');
    lineRow.className = 'passage-line-row';
    lineRow.dataset.lineId = line.id;
    lineRow.dataset.lineN = line.n;

    // Col 1: Margin number
    const marginCol = document.createElement('div');
    marginCol.className = 'line-margin-no';
    marginCol.textContent = (line.margin && line.margin % 5 === 0) ? line.margin : (line.n % 5 === 0 ? line.n : '');

    // Col 2: Speaker
    const speakerCol = document.createElement('div');
    speakerCol.className = 'line-speaker';
    speakerCol.textContent = line.speaker || '';

    // Col 3: Spoken Body with Tokens
    const bodyCol = document.createElement('div');
    bodyCol.className = 'line-body';

    if (line.direction && line.direction.text) {
      const inlineDir = document.createElement('span');
      inlineDir.className = 'inline-direction';
      inlineDir.textContent = `${line.direction.text} `;
      bodyCol.appendChild(inlineDir);
    }

    if (line.tokens && line.tokens.length) {
      line.tokens.forEach(tok => {
        const tokSpan = document.createElement('span');
        tokSpan.className = 'greek-token';
        tokSpan.textContent = tok.surface + ' ';
        tokSpan.dataset.tokenId = tok.id;
        tokSpan.dataset.norm = tok.norm;

        if (tok.entry_ids && tok.entry_ids.length) {
          tokSpan.classList.add('has-vocab');
        }

        tokSpan.addEventListener('click', () => {
          document.querySelectorAll('.greek-token').forEach(t => t.classList.remove('selected'));
          tokSpan.classList.add('selected');
          showWordCard(tok, line);
        });

        bodyCol.appendChild(tokSpan);
      });
    } else if (line.greek) {
      bodyCol.textContent = line.greek;
    }

    lineRow.appendChild(marginCol);
    lineRow.appendChild(speakerCol);
    lineRow.appendChild(bodyCol);
    linesContainer.appendChild(lineRow);
  });

  // Figures
  const figContainer = document.getElementById('passage-figures-container');
  figContainer.innerHTML = '';
  if (passage.figures && passage.figures.length) {
    passage.figures.forEach(fig => {
      const fCard = document.createElement('div');
      fCard.className = 'figure-card';
      fCard.innerHTML = `
        <div class="figure-caption">Illustration: ${fig.caption || 'ἐμβάδες'}</div>
        <button class="btn secondary-btn view-fig-btn" data-page="${fig.src.pdf_page}">View in original book (p. ${fig.src.printed_page})</button>
      `;
      fCard.querySelector('.view-fig-btn').addEventListener('click', () => {
        openProofread('text', fig.src.pdf_page);
      });
      figContainer.appendChild(fCard);
    });
  }

  // Vocab list below text (3 columns)
  renderPassageVocab(passage);
}

function renderPassageVocab(passage) {
  const container = document.getElementById('passage-vocab-columns');
  container.innerHTML = '';

  const vocabEntries = currentVocabData.filter(v => v.where && v.where.passage === passage.id);
  if (!vocabEntries.length) {
    container.innerHTML = '<p class="text-muted">No specific page vocabulary entries recorded for this passage.</p>';
    return;
  }

  vocabEntries.forEach(entry => {
    const item = document.createElement('div');
    item.className = 'vocab-col-item';
    item.innerHTML = `
      <div class="vocab-col-head">${entry.display} ${entry.article ? `<small>(${entry.article})</small>` : ''}</div>
      <div class="vocab-col-gloss">${entry.gloss_en} ${entry.lemma_display ? `<em>(${entry.lemma_display})</em>` : ''}</div>
    `;
    item.addEventListener('click', () => {
      showVocabCardDirect(entry);
    });
    container.appendChild(item);
  });
}

function showWordCard(token, line) {
  const drawer = document.getElementById('word-card-drawer');
  drawer.classList.remove('hidden');

  document.getElementById('card-surface').textContent = token.surface.replace(/[.,;·]/g, '');

  let matchedVocab = null;
  if (token.entry_ids && token.entry_ids.length) {
    matchedVocab = currentVocabData.find(v => v.id === token.entry_ids[0]);
  }
  if (!matchedVocab) {
    matchedVocab = currentVocabData.find(v => v.plain === token.norm || (v.where && v.where.passage === activePassageId && v.plain.startsWith(token.norm.slice(0, 3))));
  }

  const badge = document.getElementById('card-tier-badge');
  const morphDiv = document.getElementById('card-morphemes');
  const lemmaSpan = document.getElementById('card-lemma');
  const glossSpan = document.getElementById('card-gloss');
  const declSpan = document.getElementById('card-decl');
  const sourceSpan = document.getElementById('card-source');

  if (matchedVocab) {
    badge.textContent = '🟢 Book-Text';
    badge.className = 'tier-badge tier-book-text';
    morphDiv.textContent = matchedVocab.display;
    lemmaSpan.textContent = matchedVocab.lemma_display || matchedVocab.lemma_plain || '—';
    glossSpan.textContent = matchedVocab.gloss_en;
    declSpan.textContent = matchedVocab.decl_code ? `Noun/Verb Type (${matchedVocab.decl_code})` : '—';
    sourceSpan.textContent = `Text page ${matchedVocab.src.printed_page} (PDF p. ${matchedVocab.src.pdf_page})`;
  } else {
    badge.textContent = '🔵 LSJ Lexicon';
    badge.className = 'tier-badge tier-lsj';
    morphDiv.textContent = token.surface;
    lemmaSpan.textContent = 'Looking up...';
    glossSpan.textContent = 'Searching LSJ Lexicon...';
    declSpan.textContent = 'Ancient Greek';
    sourceSpan.textContent = `Text passage ${activePassageId}, line ${line.n}`;
  }

  // Trigger LSJ Lookup (offline cache + online fallback)
  const queryLemma = matchedVocab ? (matchedVocab.lemma_plain || matchedVocab.lemma_display) : null;
  queryLSJ(token.surface, queryLemma);

  // Grammar link
  const gramLink = document.getElementById('card-grammar-link');
  gramLink.onclick = (e) => {
    e.preventDefault();
    document.querySelector('[data-tab="grammar"]').click();
  };

  // View original page button
  const pageBtn = document.getElementById('card-view-page-btn');
  pageBtn.onclick = () => {
    openProofread('text', line.src.pdf_page);
  };

  // Check Guide note for this line
  const noteBox = document.getElementById('card-guide-note-box');
  const noteText = document.getElementById('card-guide-note-text');
  if (currentGuideData && currentGuideData.notes) {
    const matchingNote = currentGuideData.notes.find(n => n.passage === activePassageId && (n.line == line.n || n.line.includes(String(line.n))));
    if (matchingNote) {
      noteBox.classList.remove('hidden');
      noteText.innerHTML = `<strong>${matchingNote.quoted}:</strong> ${matchingNote.text}`;
    } else {
      noteBox.classList.add('hidden');
    }
  } else {
    noteBox.classList.add('hidden');
  }
}

function showVocabCardDirect(vocab) {
  const drawer = document.getElementById('word-card-drawer');
  drawer.classList.remove('hidden');

  document.getElementById('card-surface').textContent = vocab.plain;
  document.getElementById('card-tier-badge').textContent = '🟢 Book-Text';
  document.getElementById('card-tier-badge').className = 'tier-badge tier-book-text';
  document.getElementById('card-morphemes').textContent = vocab.display;
  document.getElementById('card-lemma').textContent = vocab.lemma_display || vocab.lemma_plain || '—';
  document.getElementById('card-gloss').textContent = vocab.gloss_en;
  document.getElementById('card-decl').textContent = vocab.decl_code ? `(${vocab.decl_code})` : '—';
  document.getElementById('card-source').textContent = `Text page ${vocab.src.printed_page} (PDF p. ${vocab.src.pdf_page})`;

  // Trigger LSJ Lookup
  queryLSJ(vocab.plain, vocab.lemma_plain || vocab.lemma_display);

  document.getElementById('card-view-page-btn').onclick = () => {
    openProofread('text', vocab.src.pdf_page);
  };
}

function initDrawerEvents() {
  document.getElementById('close-card-btn').addEventListener('click', () => {
    document.getElementById('word-card-drawer').classList.add('hidden');
    document.querySelectorAll('.greek-token').forEach(t => t.classList.remove('selected'));
  });
}

function initToggles() {
  const morphemeToggle = document.getElementById('toggle-morphemes');
  morphemeToggle.addEventListener('change', (e) => {
    document.getElementById('passage-lines-container').classList.toggle('morpheme-enabled', e.target.checked);
  });

  const testModeToggle = document.getElementById('toggle-test-mode');
  testModeToggle.addEventListener('change', (e) => {
    document.getElementById('passage-lines-container').classList.toggle('test-mode', e.target.checked);
  });

  const stageDirsToggle = document.getElementById('toggle-stage-dirs');
  stageDirsToggle.addEventListener('change', (e) => {
    document.querySelectorAll('.stage-direction-row, .inline-direction').forEach(el => {
      el.style.display = e.target.checked ? '' : 'none';
    });
  });

  const transToggle = document.getElementById('toggle-translation');
  transToggle.addEventListener('change', (e) => {
    if (e.target.checked) {
      document.querySelector('[data-tab="guide"]').click();
    }
  });

  const notesToggle = document.getElementById('toggle-guide-notes');
  notesToggle.addEventListener('change', (e) => {
    if (e.target.checked) {
      document.querySelector('[data-tab="guide"]').click();
    }
  });
}
