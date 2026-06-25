/* ══════════════════════════════════════
   MVPT-4 — Frontend JS
   ══════════════════════════════════════ */

'use strict';

// ── État local ──
const state = {
  sessionId: null,
  answers: {},        // { "1": "A", "2": "—", ... }
  selectedSessionId: null,
};

// Initialiser les réponses à '—'
for (let n = 1; n <= 45; n++) state.answers[String(n)] = '—';

// ══════════════════════════════════════
//  NAVIGATION TABS
// ══════════════════════════════════════
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    if (btn.dataset.tab === 'sessions') loadSessions();
  });
});

function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.tab === name));
  document.querySelectorAll('.tab-content').forEach(t =>
    t.classList.toggle('active', t.id === 'tab-' + name));
  if (name === 'sessions') loadSessions();
}

// ══════════════════════════════════════
//  SAISIE DATE AVEC MASQUE
// ══════════════════════════════════════
function setupDateInput(input) {
  // Affiche "JJ/MM/AAAA" en gris au départ
  input.addEventListener('focus', () => {
    if (!input.value) input.value = '';
  });

  input.addEventListener('input', () => {
    let raw = input.value.replace(/\D/g, '');
    let out = '';
    if (raw.length >= 1) out = raw.substring(0, 2);
    if (raw.length >= 3) out += '/' + raw.substring(2, 4);
    if (raw.length >= 5) out += '/' + raw.substring(4, 8);
    input.value = out;
    updateAge();
  });

  input.addEventListener('keydown', e => {
    if (e.key === 'Backspace') {
      // Supprimer aussi le slash si cursor est après
      const pos = input.selectionStart;
      if (pos > 0 && input.value[pos - 1] === '/') {
        input.value = input.value.slice(0, pos - 1) + input.value.slice(pos);
        input.setSelectionRange(pos - 1, pos - 1);
        e.preventDefault();
        updateAge();
      }
    }
  });
}

document.querySelectorAll('.date-input').forEach(setupDateInput);

// ══════════════════════════════════════
//  AGE
// ══════════════════════════════════════
function updateAge() {
  const dob  = document.getElementById('patient-dob').value;
  const test = document.getElementById('patient-testdate').value;
  const el   = document.getElementById('age-display');
  if (dob.length === 10 && test.length === 10) {
    const parts_dob  = dob.split('/');
    const parts_test = test.split('/');
    const d1 = new Date(+parts_dob[2],  +parts_dob[1]-1,  +parts_dob[0]);
    const d2 = new Date(+parts_test[2], +parts_test[1]-1, +parts_test[0]);
    if (!isNaN(d1) && !isNaN(d2) && d2 > d1) {
      let y = d2.getFullYear() - d1.getFullYear();
      let m = d2.getMonth() - d1.getMonth();
      if (m < 0) { y--; m += 12; }
      el.textContent = `Âge : ${y} ans ${m} mois (${(y + m/12).toFixed(2)})`;
      return;
    }
  }
  el.textContent = 'Âge : — (saisir JJ/MM/AAAA)';
}

// ══════════════════════════════════════
//  BOUTONS A/B/C/D
// ══════════════════════════════════════
document.querySelectorAll('.abcd-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const num    = btn.dataset.num;
    const choice = btn.dataset.choice;
    const current = state.answers[num];
    const newVal  = (current === choice) ? '—' : choice;
    state.answers[num] = newVal;
    applyItemStyle(num, newVal);
    updateProgress();
  });
});

function applyItemStyle(num, choice) {
  const cell     = document.getElementById('cell-' + num);
  const correct  = window.CORRECT_ANSWERS[num];
  const btns     = cell.querySelectorAll('.abcd-btn');

  cell.classList.remove('correct', 'wrong');
  if (choice === '—') {
    // neutre
  } else if (choice === correct) {
    cell.classList.add('correct');
  } else {
    cell.classList.add('wrong');
  }

  btns.forEach(b => {
    b.classList.remove('selected-correct', 'selected-wrong');
    if (b.dataset.choice === choice) {
      b.classList.add(choice === correct ? 'selected-correct' : 'selected-wrong');
    }
  });
}

// ══════════════════════════════════════
//  PROGRESSION
// ══════════════════════════════════════
function updateProgress() {
  const answered = Object.values(state.answers).filter(v => v !== '—').length;
  const name  = document.getElementById('patient-name').value.trim();
  const dob   = document.getElementById('patient-dob').value;
  const test  = document.getElementById('patient-testdate').value;
  const meta  = (name ? 1 : 0) + (dob.length === 10 ? 1 : 0) + (test.length === 10 ? 1 : 0);
  const pct   = Math.round(meta / 3 * 20 + answered / 45 * 80);
  document.getElementById('progress-fill').style.width = pct + '%';
  document.getElementById('progress-label').textContent = `${pct}% (${answered}/45 items)`;
  setStatus(`${answered}/45 items renseignés`);
}

document.getElementById('patient-name').addEventListener('input', updateProgress);

// ══════════════════════════════════════
//  CALCULER
// ══════════════════════════════════════
async function calculate() {
  const dob  = document.getElementById('patient-dob').value;
  const test = document.getElementById('patient-testdate').value;
  if (dob.length < 10 || test.length < 10) {
    alert('Veuillez saisir la date de naissance et la date du test au format JJ/MM/AAAA.');
    return;
  }

  const res = await fetch('/api/calculate', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ dob, testdate: test, answers: state.answers })
  });
  if (!res.ok) { alert('Erreur de calcul.'); return; }
  const data = await res.json();

  // Afficher résultats
  const name = document.getElementById('patient-name').value || 'Patient';
  const exam = document.getElementById('patient-examiner').value;
  document.getElementById('res-name').textContent = name;
  document.getElementById('res-meta').textContent =
    `Né(e) le ${dob} · Test : ${test} · Âge : ${data.age_years} ans ${data.age_months} mois`
    + (exam ? ` · Examinateur : ${exam}` : '');

  document.getElementById('res-raw').textContent   = data.raw;
  document.getElementById('res-std').textContent   = data.standard_score_display;
  document.getElementById('res-age-col').textContent = data.age_col;
  document.getElementById('res-pct').textContent   =
    data.percentile + (typeof data.percentile === 'number' ? 'e' : '');
  document.getElementById('res-age-eq').textContent = data.age_equiv;

  const badge = document.getElementById('interp-badge');
  badge.textContent = data.interpretation_label;
  badge.className = 'badge ' + data.interpretation_color;
  document.getElementById('interp-text').textContent = data.interpretation_text;

  // Sous-domaines
  const subsKeys = window.SECTIONS_KEYS;
  subsKeys.forEach(key => {
    const score = data.sub_scores[key];
    const total = document.getElementById('score-' + key).textContent.split('/')[1];
    const ratio = score / +total;
    const fill  = document.getElementById('bar-' + key);
    fill.style.width = (ratio * 100) + '%';
    fill.style.background = score >= 5 ? 'var(--green)' : score >= 3 ? 'var(--orange)' : 'var(--red)';
    document.getElementById('score-' + key).textContent = score + '/' + total;
  });

  document.getElementById('res-notes').textContent =
    document.getElementById('patient-notes').value || '(aucune note)';

  // Sauvegarder silencieusement
  await saveSession({ raw_score: data.raw, standard_score: data.standard_score });
  switchTab('results');
  setStatus(`Résultats calculés — Score brut : ${data.raw} · Score standard : ${data.standard_score_display}`);
}

document.getElementById('btn-calculate').addEventListener('click', calculate);

// ══════════════════════════════════════
//  SAUVEGARDER
// ══════════════════════════════════════
async function saveSession(extra = {}) {
  const payload = {
    id:           state.sessionId,
    patient_name: document.getElementById('patient-name').value,
    dob:          document.getElementById('patient-dob').value,
    testdate:     document.getElementById('patient-testdate').value,
    examiner:     document.getElementById('patient-examiner').value,
    notes:        document.getElementById('patient-notes').value,
    answers:      state.answers,
    ...extra
  };

  const answered = Object.values(state.answers).filter(v => v !== '—').length;
  if (answered === 0 && !payload.patient_name.trim()) return;

  const res  = await fetch('/api/sessions', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  state.sessionId = data.id;
  setStatus(`Session sauvegardée — ${data.saved_at.substring(11, 16)}`);
}

document.getElementById('btn-save').addEventListener('click',  () => saveSession());
document.getElementById('btn-save2').addEventListener('click', () => saveSession());

// ══════════════════════════════════════
//  NOUVEAU PATIENT
// ══════════════════════════════════════
function newSession() {
  if (!confirm('Démarrer un nouveau test ?\nLa session actuelle sera sauvegardée.')) return;
  saveSession();
  state.sessionId = null;
  state.answers   = {};
  for (let n = 1; n <= 45; n++) state.answers[String(n)] = '—';

  document.getElementById('patient-name').value     = '';
  document.getElementById('patient-dob').value      = '';
  document.getElementById('patient-examiner').value = '';
  document.getElementById('patient-notes').value    = '';
  // Date du test = aujourd'hui
  const today = new Date();
  document.getElementById('patient-testdate').value =
    String(today.getDate()).padStart(2,'0') + '/' +
    String(today.getMonth()+1).padStart(2,'0') + '/' +
    today.getFullYear();

  document.getElementById('age-display').textContent = 'Âge : —';

  for (let n = 1; n <= 45; n++) applyItemStyle(String(n), '—');
  updateProgress();
  switchTab('test');
  setStatus('Nouveau test démarré.');
}

document.getElementById('btn-new').addEventListener('click', newSession);

// ══════════════════════════════════════
//  SESSIONS — LISTE
// ══════════════════════════════════════
async function loadSessions() {
  const q      = document.getElementById('search-input').value;
  const status = document.querySelector('input[name="status-filter"]:checked').value;
  const sort   = document.getElementById('sort-select').value;

  const params = new URLSearchParams({ q, status, sort });
  const res    = await fetch('/api/sessions?' + params);
  const sessions = await res.json();

  const tbody = document.getElementById('sessions-body');
  tbody.innerHTML = '';
  sessions.forEach(s => {
    const answered = Object.values(s.answers || {}).filter(v => v !== '—').length;
    const tr = document.createElement('tr');
    if (answered < 45) tr.classList.add('tag-partial');
    if (s.id === state.selectedSessionId) tr.classList.add('selected');
    tr.dataset.id = s.id;
    const saved = (s.saved_at || '').substring(0, 16).replace('T', ' ');
    const ss = s.standard_score;
    const ssDisp = ss === null ? '—' : ss <= 54 ? '<55' : ss >= 146 ? '>145' : String(ss);
    tr.innerHTML = `
      <td>${esc(s.patient_name || '—')}</td>
      <td>${esc(s.dob || '—')}</td>
      <td>${esc(s.testdate || '—')}</td>
      <td>${esc(String(s.raw_score ?? '—'))}</td>
      <td>${ssDisp}</td>
      <td>${answered}/45</td>
      <td>${saved}</td>`;
    tr.addEventListener('click', () => {
      state.selectedSessionId = s.id;
      tbody.querySelectorAll('tr').forEach(r => r.classList.remove('selected'));
      tr.classList.add('selected');
    });
    tr.addEventListener('dblclick', () => loadSelectedSession(s.id));
    tbody.appendChild(tr);
  });

  // Compteur
  document.getElementById('search-count').textContent =
    sessions.length ? `${sessions.length} session(s)` : 'Aucun résultat';
}

// ── Charger session ──
async function loadSelectedSession(sid) {
  const id = sid || state.selectedSessionId;
  if (!id) { alert('Sélectionnez une session.'); return; }

  const res = await fetch('/api/sessions/' + id);
  if (!res.ok) { alert('Session introuvable.'); return; }
  const s = await res.json();

  state.sessionId = s.id;
  state.answers   = {};
  for (let n = 1; n <= 45; n++) state.answers[String(n)] = '—';
  Object.assign(state.answers, s.answers || {});

  document.getElementById('patient-name').value     = s.patient_name || '';
  document.getElementById('patient-dob').value      = s.dob || '';
  document.getElementById('patient-testdate').value = s.testdate || '';
  document.getElementById('patient-examiner').value = s.examiner || '';
  document.getElementById('patient-notes').value    = s.notes || '';

  updateAge();
  for (let n = 1; n <= 45; n++) applyItemStyle(String(n), state.answers[String(n)]);
  updateProgress();
  switchTab('test');
  setStatus(`Session chargée : ${s.patient_name || '—'}`);
}

// ── Supprimer session ──
async function deleteSelectedSession() {
  if (!state.selectedSessionId) { alert('Sélectionnez une session.'); return; }
  if (!confirm('Supprimer cette session ?')) return;
  await fetch('/api/sessions/' + state.selectedSessionId, { method: 'DELETE' });
  if (state.sessionId === state.selectedSessionId) state.sessionId = null;
  state.selectedSessionId = null;
  loadSessions();
  setStatus('Session supprimée.');
}

document.getElementById('btn-load-session').addEventListener('click', () => loadSelectedSession());
document.getElementById('btn-delete-session').addEventListener('click', deleteSelectedSession);

// ── Recherche & filtres ──
document.getElementById('search-input').addEventListener('input', loadSessions);
document.querySelectorAll('input[name="status-filter"]').forEach(r =>
  r.addEventListener('change', loadSessions));
document.getElementById('sort-select').addEventListener('change', loadSessions);
document.getElementById('search-clear').addEventListener('click', () => {
  document.getElementById('search-input').value = '';
  loadSessions();
});

// ══════════════════════════════════════
//  EXPORT / IMPORT
// ══════════════════════════════════════
document.getElementById('btn-export').addEventListener('click', () => {
  window.location.href = '/api/export';
});

document.getElementById('import-file').addEventListener('change', async e => {
  const file = e.target.files[0];
  if (!file) return;
  const form = new FormData();
  form.append('file', file);
  const res  = await fetch('/api/import', { method: 'POST', body: form });
  const data = await res.json();
  if (data.error) { alert('Erreur : ' + data.error); return; }
  setStatus(`${data.imported} session(s) importée(s).`);
  loadSessions();
  e.target.value = '';
});

// ══════════════════════════════════════
//  IMPRESSION
// ══════════════════════════════════════
document.getElementById('btn-print').addEventListener('click', () => {
  if (!state.sessionId) { alert('Sauvegardez d\'abord la session.'); return; }
  window.open('/rapport/' + state.sessionId, '_blank');
});

// ══════════════════════════════════════
//  UTILITAIRES
// ══════════════════════════════════════
function setStatus(msg) {
  document.getElementById('status-bar').textContent = msg;
}

function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── Init ──
const today = new Date();
document.getElementById('patient-testdate').value =
  String(today.getDate()).padStart(2,'0') + '/' +
  String(today.getMonth()+1).padStart(2,'0') + '/' +
  today.getFullYear();
updateProgress();
