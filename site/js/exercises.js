/**
 * Reading Greek — Interactive Exercises & Polytonic Keyboard Module
 */

import { state } from './app.js';

let currentExercises = [];
let currentAnswers = [];
let activeExercise = null;
let activeInputEl = null;

export function initExercises(grammarData, guideData) {
  currentExercises = grammarData.exercises || [];
  currentAnswers = guideData.answers || [];

  const listEl = document.getElementById('exercises-list');
  listEl.innerHTML = '';

  if (!currentExercises.length) {
    document.getElementById('exercise-instruction').textContent = 'No exercises loaded for this section.';
    return;
  }

  currentExercises.forEach((ex, idx) => {
    const li = document.createElement('li');
    li.className = `exercise-nav-item ${idx === 0 ? 'active' : ''}`;
    li.textContent = ex.id;
    li.addEventListener('click', () => {
      document.querySelectorAll('.exercise-nav-item').forEach(el => el.classList.remove('active'));
      li.classList.add('active');
      renderExercise(ex);
    });
    listEl.appendChild(li);
  });

  initKeyboard();

  // Load first exercise
  renderExercise(currentExercises[0]);
}

function renderExercise(exercise) {
  activeExercise = exercise;
  document.getElementById('exercise-title').textContent = `Exercise ${exercise.id}`;
  document.getElementById('exercise-instruction').textContent = exercise.instruction || 'Translate or conjugate as directed.';

  const stream = document.getElementById('exercise-items-stream');
  stream.innerHTML = '';

  if (!exercise.items || !exercise.items.length) {
    stream.innerHTML = '<p class="text-muted">No individual items recorded for this exercise.</p>';
    return;
  }

  exercise.items.forEach((item, idx) => {
    const itemCard = document.createElement('div');
    itemCard.className = 'exercise-item-card';

    const itemKey = `${exercise.id}_${item.n || idx + 1}`;
    const userGrade = state.progress[itemKey] || null;

    itemCard.innerHTML = `
      <div class="exercise-item-prompt">
        <strong>${item.n || idx + 1}.</strong> ${item.prompt}
      </div>
      <div class="exercise-answer-row">
        <input type="text" class="exercise-input" data-key="${itemKey}" placeholder="Type Greek or English answer...">
        <button class="btn secondary-btn check-ans-btn">Show Answer</button>
      </div>
      <div class="answer-key-box hidden">
        <div class="guide-answer-content"></div>
        <div class="grade-actions">
          <span>Self-grade:</span>
          <button class="btn icon-btn grade-btn ${userGrade === 'correct' ? 'active' : ''}" data-grade="correct" title="Correct">✔</button>
          <button class="btn icon-btn grade-btn ${userGrade === 'partial' ? 'active' : ''}" data-grade="partial" title="Partial">~</button>
          <button class="btn icon-btn grade-btn ${userGrade === 'review' ? 'active' : ''}" data-grade="review" title="Needs Review">✖</button>
        </div>
      </div>
    `;

    const input = itemCard.querySelector('.exercise-input');
    input.addEventListener('focus', () => {
      activeInputEl = input;
    });

    const checkBtn = itemCard.querySelector('.check-ans-btn');
    const answerBox = itemCard.querySelector('.answer-key-box');
    const answerContent = itemCard.querySelector('.guide-answer-content');

    // Find Guide answer
    const matchingAns = currentAnswers.find(a => a.exercise_id === exercise.id && a.item == (item.n || idx + 1));
    const guideAnswerText = matchingAns ? matchingAns.answer : '(See Guide answer key for this section)';

    checkBtn.addEventListener('click', () => {
      answerBox.classList.remove('hidden');
      answerContent.innerHTML = `<strong>Guide Answer:</strong> ${guideAnswerText}`;
    });

    // Grade buttons
    itemCard.querySelectorAll('.grade-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const grade = btn.dataset.grade;
        state.progress[itemKey] = grade;
        localStorage.setItem('rg_progress', JSON.stringify(state.progress));

        itemCard.querySelectorAll('.grade-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });

    stream.appendChild(itemCard);
  });
}

function initKeyboard() {
  document.querySelectorAll('.polytonic-keyboard .key').forEach(key => {
    key.addEventListener('click', (e) => {
      e.preventDefault();
      if (!activeInputEl) {
        // Default to first input on page
        activeInputEl = document.querySelector('.exercise-input');
      }
      if (!activeInputEl) return;

      const char = key.dataset.char || key.textContent.trim();
      if (key.id === 'kbd-backspace') {
        activeInputEl.value = activeInputEl.value.slice(0, -1);
      } else {
        activeInputEl.value += char;
      }
      activeInputEl.focus();
    });
  });
}
