/**
 * Reading Greek — Grammar Module
 */

export function initGrammar(grammarData) {
  const tocList = document.getElementById('grammar-toc-list');
  const streamContainer = document.getElementById('grammar-stream');

  tocList.innerHTML = '';
  streamContainer.innerHTML = '';

  if (!grammarData || !grammarData.blocks || !grammarData.blocks.length) {
    streamContainer.innerHTML = '<p>No grammar data available for this section.</p>';
    return;
  }

  // Header info
  const headerBlock = document.createElement('div');
  headerBlock.className = 'grammar-unit-header';
  headerBlock.innerHTML = `
    <h2>${grammarData.label_new || 'Section Grammar'}</h2>
    ${grammarData.label_old ? `<p class="text-muted"><em>(${grammarData.label_old})</em></p>` : ''}
    <p>Paragraphs §${grammarData.para_range[0]} – §${grammarData.para_range[1]}</p>
    <hr style="margin: 1rem 0; border: none; border-top: 1px solid var(--border-color);">
  `;
  streamContainer.appendChild(headerBlock);

  grammarData.blocks.forEach((block, idx) => {
    const bType = block.t;

    if (bType === 'para') {
      const pEl = document.createElement('div');
      pEl.className = 'grammar-block para-block';
      pEl.id = block.no ? `grammar-${block.no}` : `grammar-p-${idx}`;

      let content = block.text || '';
      // Format paragraph numbers like 130.
      if (block.no) {
        content = `<strong>${block.no}.</strong> ${content}`;
        // Add to TOC
        const li = document.createElement('li');
        li.innerHTML = `<a href="#grammar-${block.no}">§${block.no} ${block.text.slice(0, 30)}...</a>`;
        tocList.appendChild(li);
      }
      pEl.innerHTML = content;
      streamContainer.appendChild(pEl);

    } else if (bType === 'box') {
      const boxEl = document.createElement('div');
      boxEl.className = `grammar-block box-${block.kind || 'note'}`;
      boxEl.innerHTML = `
        <h4 style="color: var(--aegean); margin-bottom: 0.5rem;">${block.title}</h4>
        <div class="box-items">${(block.items || []).join('<br>')}</div>
      `;
      streamContainer.appendChild(boxEl);

    } else if (bType === 'table' && block.table) {
      const tableWrap = document.createElement('div');
      tableWrap.className = 'grammar-table-container';

      if (block.caption) {
        const cap = document.createElement('h4');
        cap.textContent = `📋 ${block.caption}`;
        tableWrap.appendChild(cap);
      }

      const tableEl = document.createElement('table');
      tableEl.className = 'paradigm-table';

      // Table Header
      if (block.table.header && Array.isArray(block.table.header) && block.table.header.length) {
        const thead = document.createElement('thead');
        block.table.header.forEach(hRow => {
          if (!Array.isArray(hRow)) return;
          const tr = document.createElement('tr');
          hRow.forEach(cell => {
            const th = document.createElement('th');
            const txt = (cell && typeof cell === 'object') ? (cell.text || '') : (cell != null ? String(cell) : '');
            th.innerHTML = formatMorphemesInTable(txt);
            tr.appendChild(th);
          });
          thead.appendChild(tr);
        });
        tableEl.appendChild(thead);
      }

      // Table Rows
      if (block.table.rows && Array.isArray(block.table.rows) && block.table.rows.length) {
        const tbody = document.createElement('tbody');
        block.table.rows.forEach(rRow => {
          if (!Array.isArray(rRow)) return;
          const tr = document.createElement('tr');
          rRow.forEach(cell => {
            const td = document.createElement('td');
            const txt = (cell && typeof cell === 'object') ? (cell.text || '') : (cell != null ? String(cell) : '');
            td.innerHTML = formatMorphemesInTable(txt);
            tr.appendChild(td);
          });
          tbody.appendChild(tr);
        });
        tableEl.appendChild(tbody);
      }

      tableWrap.appendChild(tableEl);
      streamContainer.appendChild(tableWrap);
    }
  });

  // Endings highlight toggle
  const endingsToggle = document.getElementById('toggle-table-endings');
  if (endingsToggle) {
    endingsToggle.addEventListener('change', (e) => {
      document.querySelectorAll('.table-morpheme-end').forEach(el => {
        el.style.backgroundColor = e.target.checked ? 'var(--ochre-light)' : '';
        el.style.fontWeight = e.target.checked ? '700' : '';
      });
    });
  }
}

function formatMorphemesInTable(text) {
  if (!text) return '';
  return text.split('\n').map(line => {
    line = line.trim();
    if (!line) return '';
    let escaped = line.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    if (escaped.includes('-') && !escaped.startsWith('‘') && !escaped.startsWith("'") && !escaped.startsWith('"') && /[α-ωΑ-Ω]/.test(escaped)) {
      const parts = escaped.split('-');
      if (parts.length === 3) {
        return `<span class="table-morpheme-aug">${parts[0]}</span>-<span class="table-morpheme-stem">${parts[1]}</span>-<span class="table-morpheme-end">${parts[2]}</span>`;
      } else if (parts.length === 2) {
        return `<span class="table-morpheme-stem">${parts[0]}</span>-<span class="table-morpheme-end">${parts[1]}</span>`;
      }
    }
    if (escaped.startsWith('‘') || escaped.startsWith("'") || escaped.startsWith('"')) {
      return `<span class="table-cell-translation">${escaped}</span>`;
    }
    return escaped;
  }).join('<br>');
}
