/**
 * Reading Greek — Global Search Module (Accent & Breathing Insensitive)
 */

import { state } from './app.js';
import { loadPassage } from './reader.js';

function normalizeSearch(str) {
  if (!str) return '';
  return str.normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .replace(/ς/g, 'σ')
            .replace(/[’']/g, '')
            .trim();
}

export function initSearch() {
  const input = document.getElementById('global-search-input');
  const clearBtn = document.getElementById('search-clear-btn');
  const modal = document.getElementById('search-modal');
  const closeBtn = modal.querySelector('.close-modal-btn');
  const resultsContainer = document.getElementById('search-results-list');

  closeBtn.addEventListener('click', () => modal.classList.add('hidden'));

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const q = input.value.trim();
      if (!q) return;
      performSearch(q, modal, resultsContainer);
    }
  });

  input.addEventListener('input', (e) => {
    clearBtn.style.display = e.target.value ? 'block' : 'none';
  });

  clearBtn.addEventListener('click', () => {
    input.value = '';
    clearBtn.style.display = 'none';
    modal.classList.add('hidden');
  });
}

function performSearch(query, modal, resultsContainer) {
  const normQ = normalizeSearch(query);
  resultsContainer.innerHTML = '';
  modal.classList.remove('hidden');

  const matches = [];

  // 1. Search in Vocabulary
  (state.vocabData || []).forEach(v => {
    const plainNorm = normalizeSearch(v.plain);
    const glossNorm = normalizeSearch(v.gloss_en);
    if (plainNorm.includes(normQ) || glossNorm.includes(normQ)) {
      matches.push({
        type: 'Vocabulary',
        title: `${v.display} — ${v.gloss_en}`,
        snippet: `Lemma: ${v.lemma_display || '—'} · Source: Text p. ${v.src.printed_page}`,
        action: () => {
          modal.classList.add('hidden');
          document.querySelector('[data-tab="vocab"]').click();
        }
      });
    }
  });

  // 2. Search in Text lines
  if (state.textData && state.textData.passages) {
    state.textData.passages.forEach(passage => {
      (passage.lines || []).forEach(l => {
        if (l.greek && normalizeSearch(l.greek).includes(normQ)) {
          matches.push({
            type: `Passage ${passage.id}`,
            title: `Line ${l.n} ${l.speaker ? `[${l.speaker}]` : ''}`,
            snippet: l.greek,
            action: () => {
              modal.classList.add('hidden');
              document.querySelector('[data-tab="read"]').click();
              loadPassage(passage.id);
            }
          });
        }
      });
    });
  }

  // 3. Search in Grammar blocks
  if (state.grammarData && state.grammarData.blocks) {
    state.grammarData.blocks.forEach(b => {
      if (b.text && normalizeSearch(b.text).includes(normQ)) {
        matches.push({
          type: 'Grammar',
          title: b.no ? `Paragraph §${b.no}` : 'Grammar Note',
          snippet: b.text.slice(0, 120) + '...',
          action: () => {
            modal.classList.add('hidden');
            document.querySelector('[data-tab="grammar"]').click();
          }
        });
      }
    });
  }

  if (!matches.length) {
    resultsContainer.innerHTML = `<p class="text-muted" style="padding: 1rem;">No results found for "<strong>${query}</strong>".</p>`;
    return;
  }

  matches.slice(0, 50).forEach(m => {
    const item = document.createElement('div');
    item.className = 'search-result-item';
    item.style.padding = '0.75rem';
    item.style.borderBottom = '1px solid var(--border-color)';
    item.style.cursor = 'pointer';
    item.innerHTML = `
      <span class="badge" style="background:var(--terracotta-light); color:var(--terracotta); font-size:0.75rem; font-weight:700;">${m.type}</span>
      <div style="font-weight:600; margin: 0.2rem 0;">${m.title}</div>
      <div style="font-size:0.88rem; color:var(--text-muted); font-family:var(--font-greek);">${m.snippet}</div>
    `;
    item.addEventListener('click', m.action);
    resultsContainer.appendChild(item);
  });
}
