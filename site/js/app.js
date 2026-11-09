/**
 * Reading Greek — App Controller & State Manager
 */

import { initReader, loadPassage } from './reader.js';
import { initGrammar } from './grammar.js';
import { initExercises } from './exercises.js';
import { initGuide } from './guide.js';
import { initVocab } from './vocab.js';
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

    console.log(`Loaded Section ${secId} successfully!`);
  } catch (err) {
    console.error(`Error loading section ${secId}:`, err);
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

  // Load initial section (Section 06)
  loadSectionData('06');
});
