/**
 * Reading Greek — Full Vocabulary Grid & Filter Module
 */

export function initVocab(vocabList) {
  const container = document.getElementById('vocab-full-list');
  const countSpan = document.getElementById('vocab-total-count');
  const searchInput = document.getElementById('vocab-search-input');

  countSpan.textContent = `(${vocabList.length} words)`;
  renderVocabCards(vocabList, container);

  searchInput.addEventListener('input', (e) => {
    const q = e.target.value.toLowerCase().trim();
    if (!q) {
      renderVocabCards(vocabList, container);
      countSpan.textContent = `(${vocabList.length} words)`;
      return;
    }

    const filtered = vocabList.filter(v => 
      v.plain.toLowerCase().includes(q) ||
      (v.display && v.display.toLowerCase().includes(q)) ||
      (v.gloss_en && v.gloss_en.toLowerCase().includes(q)) ||
      (v.lemma_plain && v.lemma_plain.toLowerCase().includes(q))
    );

    countSpan.textContent = `(${filtered.length} of ${vocabList.length})`;
    renderVocabCards(filtered, container);
  });
}

function renderVocabCards(list, container) {
  container.innerHTML = '';
  if (!list.length) {
    container.innerHTML = '<p class="text-muted">No matching vocabulary found.</p>';
    return;
  }

  list.forEach(v => {
    const card = document.createElement('div');
    card.className = 'vocab-grid-card';
    card.style.background = 'var(--bg-surface)';
    card.style.border = '1px solid var(--border-color)';
    card.style.borderRadius = 'var(--radius)';
    card.style.padding = '0.85rem';
    card.style.display = 'flex';
    card.style.flexDirection = 'column';
    card.style.gap = '0.3rem';

    card.innerHTML = `
      <div style="font-family: var(--font-greek); font-size: 1.25rem; font-weight: 700; color: var(--terracotta);">
        ${v.display} ${v.article ? `<small style="font-size:0.9rem; color:var(--text-muted);">(${v.article})</small>` : ''}
      </div>
      <div style="font-size: 0.95rem; color: var(--text-main); font-weight: 500;">${v.gloss_en}</div>
      ${v.lemma_display ? `<div style="font-size: 0.85rem; color: var(--aegean);">Lemma: <em>${v.lemma_display}</em></div>` : ''}
      <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: auto;">
        ${v.where ? `Passage ${v.where.passage} · ` : ''}p. ${v.src.printed_page}
      </div>
    `;
    container.appendChild(card);
  });
}
