/**
 * Reading Greek — Proofread Mode (Split-Screen Original Page vs Data)
 */

export function initProofread() {
  const container = document.getElementById('proofread-view');
  const toggleBtn = document.getElementById('proofread-toggle');
  const closeBtn = document.getElementById('proof-close-btn');
  const loadBtn = document.getElementById('proof-load-btn');
  const verifyBtn = document.getElementById('proof-verify-btn');

  toggleBtn.addEventListener('click', () => {
    container.classList.remove('hidden');
    loadPageInProofread('text', 94);
  });

  closeBtn.addEventListener('click', () => {
    container.classList.add('hidden');
  });

  loadBtn.addEventListener('click', () => {
    const book = document.getElementById('proof-book-select').value;
    const page = parseInt(document.getElementById('proof-page-input').value, 10);
    loadPageInProofread(book, page);
  });

  verifyBtn.addEventListener('click', () => {
    const book = document.getElementById('proof-book-select').value;
    const page = parseInt(document.getElementById('proof-page-input').value, 10);
    alert(`Page ${book.toUpperCase()} p. ${page} marked verified!`);
  });
}

export function openProofread(book, pdfPage) {
  const container = document.getElementById('proofread-view');
  container.classList.remove('hidden');

  document.getElementById('proof-book-select').value = book;
  document.getElementById('proof-page-input').value = pdfPage;

  loadPageInProofread(book, pdfPage);
}

async function loadPageInProofread(book, pdfPage) {
  const prefix = window.location.pathname.endsWith('/site/') || window.location.pathname.endsWith('/site/index.html') ? '../' : (window.location.pathname.includes('/site') ? '../' : './');
  const imgEl = document.getElementById('proof-image');
  const pad = String(pdfPage).padStart(3, '0');
  imgEl.src = `${prefix}work/pages/${book}/p${pad}_300dpi.png`;
  imgEl.onerror = () => {
    imgEl.src = `${prefix}work/pages/${book}/p${pad}_120dpi.png`;
  };

  const metaEl = document.getElementById('proof-meta-info');
  const blocksEl = document.getElementById('proof-blocks-stream');
  blocksEl.innerHTML = '<p>Loading transcription...</p>';

  try {
    let res = await fetch(`${prefix}data/pages/${book}/p${pad}.json`);
    if (!res.ok) res = await fetch(`../data/pages/${book}/p${pad}.json`);
    if (!res.ok) res = await fetch(`./data/pages/${book}/p${pad}.json`);
    if (!res.ok) {
      blocksEl.innerHTML = `<p class="text-muted">No raw JSON transcription cached for ${book} p. ${pdfPage}.</p>`;
      metaEl.innerHTML = `<strong>${book.toUpperCase()} PDF Page ${pdfPage}</strong>`;
      return;
    }

    const data = await res.json();
    metaEl.innerHTML = `
      <strong>${book.toUpperCase()} PDF Page ${pdfPage}</strong> · Printed Folio: ${data.folio || '—'} · Running Head: <em>${data.running_head || '—'}</em>
      <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.25rem;">Total Blocks: ${data.blocks ? data.blocks.length : 0}</div>
    `;

    blocksEl.innerHTML = '';
    (data.blocks || []).forEach((b, idx) => {
      const bDiv = document.createElement('div');
      bDiv.className = 'proof-block-item';
      bDiv.innerHTML = `
        <div class="proof-block-header">${b.type} ${b.speaker ? `· [${b.speaker}]` : ''} ${b.margin_number ? `· line ${b.margin_number}` : ''}</div>
        <textarea style="width:100%; min-height:50px; font-family:var(--font-greek); font-size:1.05rem; padding:0.4rem; border:1px solid var(--border-color); border-radius:4px;">${b.text || b.caption || ''}</textarea>
      `;
      blocksEl.appendChild(bDiv);
    });

  } catch (err) {
    blocksEl.innerHTML = `<p>Error loading page JSON: ${err.message}</p>`;
  }
}
