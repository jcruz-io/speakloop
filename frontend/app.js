const API_BASE = '';

// ── State ─────────────────────────────────────────────────────────────────────

const SECTIONS = ['section-setup', 'section-practice', 'section-loading', 'section-feedback'];

function showSection(id) {
  SECTIONS.forEach((s) => {
    document.getElementById(s).classList.toggle('hidden', s !== id);
  });
}

// ── Setup form ────────────────────────────────────────────────────────────────

let generatedText = '';

document.getElementById('setup-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const role = document.getElementById('input-role').value.trim();
  const interests = document.getElementById('input-interests').value
    .split(',').map((s) => s.trim()).filter(Boolean);
  const target_length = parseInt(document.getElementById('input-length').value, 10);

  const btn = document.getElementById('btn-generate');
  btn.disabled = true;
  btn.innerHTML = `
    <span class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
    Generating…`;

  try {
    const res = await fetch(`${API_BASE}/api/v1/practice-texts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role, interests, target_length }),
    });

    if (!res.ok) throw new Error(`Server responded with status ${res.status}`);

    const data = await res.json();
    generatedText = data.content;
    document.getElementById('practice-text').textContent = generatedText;
    showSection('section-practice');
  } catch (err) {
    alert(`Could not generate text. Is the backend running?\n\n${err.message}`);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i class="ph ph-sparkle text-lg"></i> Generate Practice Text';
  }
});

// ── Recording ─────────────────────────────────────────────────────────────────

let mediaRecorder = null;
let audioChunks = [];

const btnRecord = document.getElementById('btn-record');
const btnStop = document.getElementById('btn-stop');
const recordingBadge = document.getElementById('recording-badge');

btnRecord.addEventListener('click', async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];

    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : MediaRecorder.isTypeSupported('audio/webm')
        ? 'audio/webm'
        : '';

    mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      const audioBlob = new Blob(audioChunks, { type: mimeType || 'audio/webm' });
      await submitEvaluation(audioBlob);
    };

    mediaRecorder.start();

    btnRecord.disabled = true;
    btnStop.disabled = false;
    recordingBadge.classList.remove('hidden');
    recordingBadge.classList.add('flex');
  } catch (err) {
    alert(`Microphone access denied or unavailable.\n\n${err.message}`);
  }
});

btnStop.addEventListener('click', () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
    btnStop.disabled = true;
    btnRecord.disabled = false;
    recordingBadge.classList.add('hidden');
    recordingBadge.classList.remove('flex');
  }
});

// ── Evaluation ────────────────────────────────────────────────────────────────

async function submitEvaluation(audioBlob) {
  showSection('section-loading');

  const formData = new FormData();
  formData.append('original_text', generatedText);
  formData.append('audio_file', audioBlob, 'recording.webm');

  try {
    const res = await fetch(`${API_BASE}/api/v1/evaluations`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) throw new Error(`Server responded with status ${res.status}`);

    const data = await res.json();
    renderFeedback(data);
    showSection('section-feedback');
  } catch (err) {
    alert(`Could not evaluate pronunciation.\n\n${err.message}`);
    showSection('section-practice');
  }
}

// ── Feedback rendering ────────────────────────────────────────────────────────

function scoreColor(score) {
  if (score >= 85) return 'text-emerald-500';
  if (score >= 60) return 'text-amber-500';
  return 'text-red-500';
}

function scoreLabel(score) {
  if (score >= 85) return { text: 'Excellent!', cls: 'text-emerald-600' };
  if (score >= 60) return { text: 'Good — keep practicing', cls: 'text-amber-600' };
  return { text: "Needs work — don't give up!", cls: 'text-red-600' };
}

function renderFeedback({ original_text, transcribed_text, accuracy_score, corrections }) {
  const rounded = Math.round(accuracy_score);

  const scoreEl = document.getElementById('accuracy-score');
  scoreEl.textContent = `${rounded}%`;
  scoreEl.className = `text-8xl font-bold mb-2 ${scoreColor(accuracy_score)}`;

  const label = scoreLabel(accuracy_score);
  const labelEl = document.getElementById('score-label');
  labelEl.textContent = label.text;
  labelEl.className = `text-sm font-semibold ${label.cls}`;

  document.getElementById('original-text').textContent = original_text;
  document.getElementById('transcribed-text').textContent = transcribed_text;

  const container = document.getElementById('corrections-container');
  container.innerHTML = '';

  if (!corrections || corrections.length === 0) {
    container.innerHTML = `
      <div class="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-2xl p-6 text-center">
        <i class="ph ph-check-circle text-3xl text-emerald-500 mb-2 block"></i>
        <p class="font-semibold text-emerald-700 dark:text-emerald-400">No corrections — perfect pronunciation!</p>
      </div>`;
    return;
  }

  const heading = document.createElement('p');
  heading.className = 'text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3 px-1';
  heading.textContent = `${corrections.length} correction${corrections.length !== 1 ? 's' : ''}`;
  container.appendChild(heading);

  corrections.forEach(({ original_word, transcribed_word, phonetic_tip, context_tip }) => {
    const card = document.createElement('div');
    card.className = 'bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-6 mb-3 space-y-3';
    card.innerHTML = `
      <div class="flex items-center gap-3 flex-wrap">
        <span class="bg-red-100 dark:bg-red-900/40 text-red-700 dark:text-red-300 text-sm font-semibold px-3 py-1 rounded-full line-through">
          ${transcribed_word}
        </span>
        <i class="ph ph-arrow-right text-slate-400 dark:text-slate-500"></i>
        <span class="bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300 text-sm font-semibold px-3 py-1 rounded-full">
          ${original_word}
        </span>
      </div>
      <div class="flex gap-3 text-sm text-slate-700 dark:text-slate-300 bg-indigo-50 dark:bg-indigo-900/30 rounded-xl p-4">
        <i class="ph ph-ear text-indigo-500 dark:text-indigo-400 text-lg shrink-0 mt-0.5"></i>
        <p>${phonetic_tip}</p>
      </div>
      <div class="flex gap-3 text-sm text-slate-700 dark:text-slate-300 bg-amber-50 dark:bg-amber-900/30 rounded-xl p-4">
        <i class="ph ph-lightbulb text-amber-500 dark:text-amber-400 text-lg shrink-0 mt-0.5"></i>
        <p>${context_tip}</p>
      </div>`;
    container.appendChild(card);
  });
}

// ── Dark mode ────────────────────────────────────────────────────────────────

const htmlEl = document.documentElement;
const themeIcon = document.getElementById('theme-icon');

function applyTheme(dark) {
  if (dark) {
    htmlEl.classList.add('dark');
    themeIcon.className = 'ph ph-sun text-slate-300 text-lg';
  } else {
    htmlEl.classList.remove('dark');
    themeIcon.className = 'ph ph-moon text-slate-600 text-lg';
  }
}

applyTheme(localStorage.getItem('speakloop-theme') === 'dark');

document.getElementById('btn-theme-toggle').addEventListener('click', () => {
  const isDark = htmlEl.classList.contains('dark');
  localStorage.setItem('speakloop-theme', isDark ? 'light' : 'dark');
  applyTheme(!isDark);
});

// ── Restart ───────────────────────────────────────────────────────────────────

function resetRecordingState() {
  audioChunks = [];
  mediaRecorder = null;
  btnRecord.disabled = false;
  btnStop.disabled = true;
  recordingBadge.classList.add('hidden');
  recordingBadge.classList.remove('flex');
}

document.getElementById('btn-try-again').addEventListener('click', () => {
  resetRecordingState();
  showSection('section-practice');
});

document.getElementById('btn-restart').addEventListener('click', () => {
  generatedText = '';
  resetRecordingState();
  document.getElementById('corrections-container').innerHTML = '';
  showSection('section-setup');
});
