/**
 * Reading Greek — Guide Notes & Translations Module
 */

export function initGuide(guideData) {
  const transContainer = document.getElementById('guide-translations-stream');
  const notesContainer = document.getElementById('guide-notes-stream');

  transContainer.innerHTML = '';
  notesContainer.innerHTML = '';

  if (!guideData) return;

  // Render translations
  if (guideData.translations && guideData.translations.length) {
    guideData.translations.forEach(tr => {
      const card = document.createElement('div');
      card.className = 'guide-translation-card';
      card.style.marginBottom = '1.5rem';
      card.style.padding = '1rem';
      card.style.backgroundColor = 'var(--bg-surface)';
      card.style.border = '1px solid var(--border-color)';
      card.style.borderRadius = 'var(--radius)';
      card.innerHTML = `
        <h4 style="color: var(--terracotta); margin-bottom: 0.5rem;">${tr.passage ? `Passage ${tr.passage}` : 'Translation'}</h4>
        <div style="font-size: 0.95rem; line-height: 1.7;">${tr.text.replace(/\n/g, '<br>')}</div>
      `;
      transContainer.appendChild(card);
    });
  } else {
    transContainer.innerHTML = '<p class="text-muted">No translations available.</p>';
  }

  // Render notes
  if (guideData.notes && guideData.notes.length) {
    guideData.notes.forEach(note => {
      const nCard = document.createElement('div');
      nCard.className = 'guide-note-item';
      nCard.style.marginBottom = '1rem';
      nCard.style.padding = '0.75rem 1rem';
      nCard.style.backgroundColor = 'var(--bg-card)';
      nCard.style.borderLeft = '3px solid var(--aegean)';
      nCard.style.borderRadius = '0 4px 4px 0';
      nCard.innerHTML = `
        <div style="font-weight: 700; color: var(--aegean); font-size: 0.9rem;">Line ${note.line}</div>
        <div style="font-family: var(--font-greek); font-size: 1.15rem; color: var(--text-main); margin: 0.2rem 0;">${note.quoted}</div>
        <div style="font-size: 0.92rem; color: var(--text-muted);">${note.text}</div>
      `;
      notesContainer.appendChild(nCard);
    });
  } else {
    notesContainer.innerHTML = '<p class="text-muted">No line notes recorded for this section.</p>';
  }
}
