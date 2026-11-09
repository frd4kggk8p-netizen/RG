/**
 * Reading Greek — Interactive Spaced Repetition Flashcards (Phase 6)
 */

import { state } from './app.js';

let fullVocabList = [];
let activeCards = [];
let currentIndex = 0;
let isFlipped = false;
let currentMode = 'gr-en'; // 'gr-en' or 'en-gr'
let masteryData = JSON.parse(localStorage.getItem('rg_flashcards') || '{}');

export function initFlashcards(vocabList, currentSection) {
  fullVocabList = vocabList || [];
  
  const sectionSelect = document.getElementById('fc-section-filter');
  const modeSelect = document.getElementById('fc-mode-filter');
  const flipBtn = document.getElementById('fc-flip-btn');
  const prevBtn = document.getElementById('fc-prev-btn');
  const nextBtn = document.getElementById('fc-next-btn');
  const shuffleBtn = document.getElementById('fc-shuffle-btn');
  const cardEl = document.getElementById('active-flashcard');

  // Filter change
  sectionSelect.addEventListener('change', (e) => {
    updateCardFilter(e.target.value);
  });

  modeSelect.addEventListener('change', (e) => {
    currentMode = e.target.value;
    renderCurrentCard();
  });

  // Card click / Flip button
  cardEl.addEventListener('click', (e) => {
    if (e.target.closest('.fc-rating-row')) return;
    toggleFlip();
  });

  flipBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleFlip();
  });

  // Navigation
  prevBtn.addEventListener('click', () => {
    if (currentIndex > 0) {
      currentIndex--;
      renderCurrentCard();
    }
  });

  nextBtn.addEventListener('click', () => {
    if (currentIndex < activeCards.length - 1) {
      currentIndex++;
      renderCurrentCard();
    }
  });

  shuffleBtn.addEventListener('click', () => {
    shuffleCards();
    currentIndex = 0;
    renderCurrentCard();
  });

  // Rating buttons
  document.querySelectorAll('.fc-rate-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const rating = btn.dataset.rate;
      handleRating(rating);
    });
  });

  // Keyboard shortcut (Space = flip, ArrowRight = next, ArrowLeft = prev)
  window.addEventListener('keydown', (e) => {
    if (state.currentTab !== 'flashcards') return;
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    if (e.code === 'Space') {
      e.preventDefault();
      toggleFlip();
    } else if (e.code === 'ArrowRight') {
      e.preventDefault();
      nextBtn.click();
    } else if (e.code === 'ArrowLeft') {
      e.preventDefault();
      prevBtn.click();
    }
  });

  // Initialize with current section
  updateCardFilter(sectionSelect.value);
}

function updateCardFilter(filterVal) {
  if (filterVal === 'all') {
    activeCards = [...fullVocabList];
  } else if (filterVal === 'current') {
    const sPrefix = state.currentSection.replace(/^0/, '');
    activeCards = fullVocabList.filter(v => v.where && v.where.passage && v.where.passage.startsWith(sPrefix));
  } else {
    const sPrefix = filterVal.replace(/^0/, '');
    activeCards = fullVocabList.filter(v => v.where && v.where.passage && v.where.passage.startsWith(sPrefix));
  }

  if (!activeCards.length) {
    activeCards = [...fullVocabList];
  }

  currentIndex = 0;
  renderCurrentCard();
}

function shuffleCards() {
  for (let i = activeCards.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [activeCards[i], activeCards[j]] = [activeCards[j], activeCards[i]];
  }
}

function toggleFlip() {
  const cardEl = document.getElementById('active-flashcard');
  isFlipped = !isFlipped;
  if (isFlipped) {
    cardEl.classList.add('flipped');
  } else {
    cardEl.classList.remove('flipped');
  }
}

function renderCurrentCard() {
  const cardEl = document.getElementById('active-flashcard');
  isFlipped = false;
  cardEl.classList.remove('flipped');

  const curIdxSpan = document.getElementById('fc-current-index');
  const totalCountSpan = document.getElementById('fc-total-count');
  const masteredCountSpan = document.getElementById('fc-mastered-count');

  totalCountSpan.textContent = activeCards.length;
  curIdxSpan.textContent = activeCards.length ? currentIndex + 1 : 0;

  // Count mastered
  const mastered = activeCards.filter(c => (masteryData[c.id] || 0) >= 3).length;
  masteredCountSpan.textContent = mastered;

  if (!activeCards.length || currentIndex >= activeCards.length) {
    document.getElementById('fc-front-text').textContent = 'No cards available';
    document.getElementById('fc-front-sub').textContent = '';
    return;
  }

  const v = activeCards[currentIndex];
  const passageInfo = v.where ? `Section ${v.where.passage}` : 'Vocabulary';
  const pageInfo = v.src ? `Text p. ${v.src.printed_page}` : '';

  document.getElementById('fc-card-badge').textContent = `${passageInfo} · ${pageInfo}`;
  document.getElementById('fc-back-badge').textContent = `${passageInfo} · Definition`;

  if (currentMode === 'gr-en') {
    // Front: Greek
    document.getElementById('fc-front-text').textContent = v.display;
    document.getElementById('fc-front-sub').textContent = v.article ? `(${v.article})` : '';

    // Back: English + Lemma
    document.getElementById('fc-back-text').textContent = v.gloss_en;
    document.getElementById('fc-back-sub').textContent = v.plain;
    document.getElementById('fc-back-details').innerHTML = `
      ${v.lemma_display ? `<div><strong>Lemma:</strong> <em>${v.lemma_display}</em></div>` : ''}
      ${v.decl_code ? `<div><strong>Type:</strong> ${v.decl_code}</div>` : ''}
      <div style="margin-top:0.5rem; font-size:0.85rem; color:var(--text-muted);">
        Mastery Level: ${getMasteryStars(masteryData[v.id] || 0)}
      </div>
    `;
  } else {
    // Front: English
    document.getElementById('fc-front-text').style.fontFamily = 'var(--font-sans)';
    document.getElementById('fc-front-text').textContent = v.gloss_en;
    document.getElementById('fc-front-sub').textContent = v.decl_code ? `Type: ${v.decl_code}` : '';

    // Back: Greek
    document.getElementById('fc-back-text').style.fontFamily = 'var(--font-greek)';
    document.getElementById('fc-back-text').textContent = v.display;
    document.getElementById('fc-back-sub').textContent = v.article ? `(${v.article})` : '';
    document.getElementById('fc-back-details').innerHTML = `
      ${v.lemma_display ? `<div><strong>Lemma:</strong> <em>${v.lemma_display}</em></div>` : ''}
      <div style="margin-top:0.5rem; font-size:0.85rem; color:var(--text-muted);">
        Mastery Level: ${getMasteryStars(masteryData[v.id] || 0)}
      </div>
    `;
  }
}

function handleRating(rating) {
  const v = activeCards[currentIndex];
  if (!v) return;

  let score = masteryData[v.id] || 0;
  if (rating === 'again') {
    score = 0;
  } else if (rating === 'hard') {
    score = Math.max(1, score);
  } else if (rating === 'good') {
    score = Math.min(3, score + 1);
  } else if (rating === 'easy') {
    score = Math.min(5, score + 2);
  }

  masteryData[v.id] = score;
  localStorage.setItem('rg_flashcards', JSON.stringify(masteryData));

  // Advance to next card
  if (currentIndex < activeCards.length - 1) {
    currentIndex++;
  } else {
    currentIndex = 0;
  }
  renderCurrentCard();
}

function getMasteryStars(score) {
  if (score >= 4) return '⭐⭐⭐⭐ (Mastered)';
  if (score === 3) return '⭐⭐⭐ (Good)';
  if (score === 2) return '⭐⭐ (Learning)';
  if (score === 1) return '⭐ (Struggling)';
  return '⚪ (New)';
}
