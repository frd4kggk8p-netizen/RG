/**
 * Reading Greek — App Controller & State Manager
 */

import { initReader, loadPassage } from './reader.js';
import { initGrammar } from './grammar.js';
import { initExercises } from './exercises.js';
import { initGuide } from './guide.js';
import { initVocab } from './vocab.js';
import { initFlashcards } from './flashcards.js';
import { initProofread, openProofread } from './proofread.js';
import { initSearch } from './search.js';

export const state = {
  currentSection: '06',
  currentTab: 'read',
  textData: null,
  grammarData: null,
  guideData: null,
  vocabData: [],
  progress: JSON.parse(localStorage.getItem('rg_progress') || '{}'),
  theme: localStorage.getItem('rg_theme') || 'light'
};

export async function loadSectionData(secId) {
  state.currentSection = secId;
  const prefix = window.location.pathname.endsWith('/site/') || window.location.pathname.endsWith('/site/index.html') ? '../' : (window.location.pathname.includes('/site') ? '../' : './');
  try {
    const fetchWithFallback = async (relPath) => {
      let r = await fetch(prefix + relPath);
      if (!r.ok) r = await fetch('../' + relPath);
      if (!r.ok) r = await fetch('./' + relPath);
      return r.ok ? r.json() : null;
    };

    const [textRes, gramRes, guideRes, vocabRes] = await Promise.all([
      fetchWithFallback(`data/text/s${secId}.json`),
      fetchWithFallback(`data/grammar/s${secId}.json`),
      fetchWithFallback(`data/guide/s${secId}.json`),
      fetchWithFallback(`data/vocab/book_text.json`)
    ]);

    state.textData = textRes;
    state.grammarData = gramRes;
    state.guideData = guideRes;
    state.vocabData = vocabRes || [];

    // Filter vocab for current section
    state.sectionVocab = state.vocabData.filter(v => v.where && v.where.passage && v.where.passage.startsWith(secId.replace(/^0/, '')));

    // Initialize/Refresh views
    if (state.textData) initReader(state.textData, state.vocabData, state.guideData);
    if (state.grammarData) initGrammar(state.grammarData);
    if (state.grammarData && state.guideData) initExercises(state.grammarData, state.guideData);
    if (state.guideData) initGuide(state.guideData);
    initVocab(state.sectionVocab.length ? state.sectionVocab : state.vocabData);
    initFlashcards(state.vocabData, secId);

    console.log(`Loaded Section ${secId} successfully!`);
  } catch (err) {
    console.error(`Error loading section ${secId}:`, err);
  }
}

let referenceData = null;

export async function openReferenceParadigm(declCode) {
  const modal = document.getElementById('reference-modal');
  const titleEl = document.getElementById('ref-modal-title');
  const bodyEl = document.getElementById('ref-modal-body');

  if (!referenceData) {
    const prefix = window.location.pathname.includes('/site') ? '../' : './';
    let r = await fetch(prefix + 'data/reference_grammar.json');
    if (!r.ok) r = await fetch('../data/reference_grammar.json');
    if (!r.ok) r = await fetch('./data/reference_grammar.json');
    if (!r.ok) r = await fetch('./site/data/reference_grammar.json');
    if (r.ok) referenceData = await r.json();
  }

  const cleanCode = (declCode || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  const pattern = referenceData && referenceData.noun_declensions ? referenceData.noun_declensions[cleanCode] : null;

  if (pattern) {
    titleEl.textContent = `Declension Pattern: ${cleanCode.toUpperCase()}`;
    let html = `
      <h4 style="color:var(--aegean); margin-bottom:0.5rem;">${pattern.name}</h4>
      <p style="margin-bottom:1rem;"><strong>Example:</strong> <span style="font-family:var(--font-greek); font-size:1.15rem; color:var(--terracotta);">${pattern.example}</span></p>
      <div class="grammar-table-container" style="margin:0;">
        <table class="paradigm-table">
          <thead>
            <tr>${pattern.table.header[0].map(h => `<th>${h}</th>`).join('')}</tr>
          </thead>
          <tbody>
            ${pattern.table.rows.map(row => `<tr>${row.map(c => `<td>${c}</td>`).join('')}</tr>`).join('')}
          </tbody>
        </table>
      </div>
    `;
    bodyEl.innerHTML = html;
  } else {
    titleEl.textContent = `Grammar Reference`;
    bodyEl.innerHTML = `<p>Reference paradigm for <code>${declCode}</code> not found in table summary.</p>`;
  }

  modal.classList.remove('hidden');
}

function initReferenceModal() {
  const modal = document.getElementById('reference-modal');
  const closeBtn = document.getElementById('close-ref-modal-btn');
  if (closeBtn) {
    closeBtn.addEventListener('click', () => modal.classList.add('hidden'));
  }
}

function initTheme() {
  document.documentElement.setAttribute('data-theme', state.theme);
  const themeBtn = document.getElementById('theme-toggle');
  themeBtn.textContent = state.theme === 'dark' ? '☼' : '☾';

  themeBtn.addEventListener('click', () => {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', state.theme);
    themeBtn.textContent = state.theme === 'dark' ? '☼' : '☾';
    localStorage.setItem('rg_theme', state.theme);
  });
}

function initTabs() {
  const tabs = document.querySelectorAll('.tab-btn');
  tabs.forEach(btn => {
    btn.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));

      btn.classList.add('active');
      const tabId = btn.dataset.tab;
      state.currentTab = tabId;
      document.getElementById(`tab-${tabId}`).classList.add('active');
    });
  });
}

function initSectionSelect() {
  const select = document.getElementById('section-select');
  select.value = state.currentSection;
  select.addEventListener('change', (e) => {
    loadSectionData(e.target.value);
  });
}

function initExport() {
  document.getElementById('export-progress-btn').addEventListener('click', () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(state.progress, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `reading_greek_progress_${new Date().toISOString().slice(0,10)}.json`);
    dlAnchor.click();
  });
}

// Global bootstrap
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initTabs();
  initSectionSelect();
  initExport();
  initProofread();
  initSearch();
  initReferenceModal();

  // Load initial section (Section 06)
  loadSectionData('06');
});
