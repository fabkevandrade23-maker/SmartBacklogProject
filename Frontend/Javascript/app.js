/* ============================================
   SmartBacklog — app.js
============================================ */

const API = 'http://127.0.0.1:8000';
let tasks = [];
let currentFilter = 'all';
let draggedId = null;

/* ─────────────────────────────
   INIT
───────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  checkAuth();
  loadSettings();
  fetchTasks();
});

/* ─────────────────────────────
   AUTH
───────────────────────────── */
function checkAuth() {
  const token = localStorage.getItem('token');
  if (!token) { window.location.href = 'login.html'; return; }
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const name = user.username || user.name || 'Utilisateur';
  document.getElementById('user-name').textContent = name;
  document.getElementById('user-avatar').textContent = name.charAt(0).toUpperCase();
}

function logout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  window.location.href = 'login.html';
}

/* ─────────────────────────────
   SETTINGS
───────────────────────────── */
function loadSettings() {
  const s = JSON.parse(localStorage.getItem('settings') || '{}');
  if (s.name)  document.getElementById('set-name').value  = s.name;
  if (s.email) document.getElementById('set-email').value = s.email;
}

function saveSettings() {
  const s = { name: document.getElementById('set-name').value, email: document.getElementById('set-email').value };
  localStorage.setItem('settings', JSON.stringify(s));
  if (s.name) {
    document.getElementById('user-name').textContent = s.name;
    document.getElementById('user-avatar').textContent = s.name.charAt(0).toUpperCase();
  }
  toast('Paramètres sauvegardés !', 'success');
}

/* ─────────────────────────────
   NAVIGATION
───────────────────────────── */
const views = ['dashboard', 'kanban', 'analytics', 'ai', 'settings'];
const viewTitles = { dashboard: 'Dashboard', kanban: 'Kanban Board', analytics: 'Analytics', ai: 'IA Prioritizer', settings: 'Paramètres' };

function showView(name) {
  views.forEach(v => {
    document.getElementById('view-' + v).style.display = v === name ? '' : 'none';
  });
  document.getElementById('view-title').textContent = viewTitles[name] || name;
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  event?.currentTarget?.classList.add('active');
  if (name === 'kanban')    renderKanban();
  if (name === 'analytics') renderAnalytics();
  if (name === 'dashboard') renderDashboard();
}

/* ─────────────────────────────
   API CALLS
───────────────────────────── */
async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('token');
  const res = await fetch(API + path, {
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json', ...options.headers },
    ...options
  });
  if (res.status === 401) { logout(); return null; }
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function fetchTasks() {
  try {
    tasks = await apiFetch('/tasks') || [];
    renderDashboard();
    document.getElementById('pending-count').textContent =
      tasks.filter(t => t.status !== 'done').length;
  } catch (e) {
    // Mode démo si le backend n'est pas lancé
    tasks = getDemoTasks();
    renderDashboard();
  }
}

function getDemoTasks() {
  return [
    { id: 1, title: 'Implémenter auth JWT', description: 'Système d\'authentification complet', priority: 'high', status: 'todo' },
    { id: 2, title: 'Dashboard analytics', description: 'Graphiques de performance', priority: 'high', status: 'inprogress' },
    { id: 3, title: 'API REST tâches', description: 'CRUD complet avec FastAPI', priority: 'medium', status: 'done' },
    { id: 4, title: 'Interface Kanban', description: 'Drag & drop des tâches', priority: 'medium', status: 'todo' },
    { id: 5, title: 'Intégration GPT-4o', description: 'Priorisation automatique', priority: 'low', status: 'inprogress' },
    { id: 6, title: 'Tests unitaires', description: 'Coverage > 80%', priority: 'low', status: 'todo' },
  ];
}

/* ─────────────────────────────
   TASK CRUD
───────────────────────────── */
async function saveTask() {
  const id    = document.getElementById('edit-task-id').value;
  const title = document.getElementById('task-title-input').value.trim();
  if (!title) { toast('Le titre est obligatoire', 'error'); return; }

  const payload = {
    title,
    description: document.getElementById('task-desc-input').value,
    priority:    document.getElementById('task-priority-input').value,
    status:      document.getElementById('task-status-input').value,
  };

  try {
    if (id) {
      await apiFetch(`/tasks/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
      tasks = tasks.map(t => t.id == id ? { ...t, ...payload } : t);
      toast('Tâche mise à jour !', 'success');
    } else {
      const created = await apiFetch('/tasks', { method: 'POST', body: JSON.stringify(payload) });
      tasks.push(created || { ...payload, id: Date.now() });
      toast('Tâche créée !', 'success');
    }
  } catch {
    const newTask = { ...payload, id: Date.now() };
    if (id) tasks = tasks.map(t => t.id == id ? newTask : t);
    else tasks.push(newTask);
    toast(id ? 'Tâche mise à jour !' : 'Tâche créée !', 'success');
  }

  closeModal('new-task');
  renderDashboard();
  renderKanban();
  document.getElementById('pending-count').textContent = tasks.filter(t => t.status !== 'done').length;
}

function editTask(id) {
  const task = tasks.find(t => t.id == id);
  if (!task) return;
  document.getElementById('edit-task-id').value          = id;
  document.getElementById('task-title-input').value      = task.title;
  document.getElementById('task-desc-input').value       = task.description || '';
  document.getElementById('task-priority-input').value   = task.priority;
  document.getElementById('task-status-input').value     = task.status;
  document.getElementById('modal-task-title').textContent = 'Modifier la tâche';
  openModal('new-task');
}

async function deleteTask(id) {
  if (!confirm('Supprimer cette tâche ?')) return;
  try { await apiFetch(`/tasks/${id}`, { method: 'DELETE' }); } catch {}
  tasks = tasks.filter(t => t.id !== id);
  renderDashboard();
  renderKanban();
  toast('Tâche supprimée', 'info');
}

async function updateTaskStatus(id, status) {
  tasks = tasks.map(t => t.id == id ? { ...t, status } : t);
  try { await apiFetch(`/tasks/${id}`, { method: 'PUT', body: JSON.stringify({ status }) }); } catch {}
  renderKanban();
  renderDashboard();
}

function clearAllTasks() {
  if (!confirm('Supprimer TOUTES les tâches ? Cette action est irréversible.')) return;
  tasks = [];
  renderDashboard();
  renderKanban();
  toast('Toutes les tâches ont été supprimées', 'info');
}

/* ─────────────────────────────
   DASHBOARD
───────────────────────────── */
function renderDashboard() {
  const total  = tasks.length;
  const done   = tasks.filter(t => t.status === 'done').length;
  const inprog = tasks.filter(t => t.status === 'inprogress').length;
  const high   = tasks.filter(t => t.priority === 'high').length;
  const pct    = total > 0 ? Math.round((done / total) * 100) : 0;

  document.getElementById('stat-total').textContent      = total;
  document.getElementById('stat-done').textContent       = done;
  document.getElementById('stat-done-pct').textContent   = `${pct}% du total`;
  document.getElementById('stat-inprogress').textContent = inprog;
  document.getElementById('stat-high').textContent       = high;

  // Progress bars
  const byPrio = (p) => tasks.filter(t => t.priority === p);
  const donePrio = (p) => byPrio(p).filter(t => t.status === 'done');

  ['high','medium','low'].forEach(p => {
    const all  = byPrio(p).length;
    const done = donePrio(p).length;
    const pct  = all > 0 ? Math.round((done / all) * 100) : 0;
    const bar  = { high: 'prog-high', medium: 'prog-med', low: 'prog-low' }[p];
    const lbl  = { high: 'prog-high-lbl', medium: 'prog-med-lbl', low: 'prog-low-lbl' }[p];
    document.getElementById(bar).style.width = pct + '%';
    document.getElementById(lbl).textContent = `${done}/${all}`;
  });

  // Recent tasks
  const container = document.getElementById('recent-tasks-list');
  const recent = [...tasks].slice(-5).reverse();
  if (!recent.length) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">📋</div><div class="empty-title">Aucune tâche</div><div class="empty-desc">Commencez par créer une tâche</div></div>`;
    return;
  }
  container.innerHTML = recent.map(t => `
    <div style="display:flex; align-items:center; gap:12px; padding:10px 0; border-bottom:1px solid var(--border);">
      <div style="flex:1; min-width:0;">
        <div style="font-size:14px; font-weight:500; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${escHtml(t.title)}</div>
        <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">${statusLabel(t.status)}</div>
      </div>
      <span class="badge badge-${t.priority}">${priorityLabel(t.priority)}</span>
    </div>`).join('');
}

/* ─────────────────────────────
   KANBAN
───────────────────────────── */
function renderKanban() {
  const statuses = ['todo', 'inprogress', 'done'];
  const filtered = currentFilter === 'all' ? tasks : tasks.filter(t => t.priority === currentFilter);

  statuses.forEach(s => {
    const col   = filtered.filter(t => t.status === s);
    const el    = document.getElementById('tasks-' + s);
    const count = document.getElementById('count-' + s);
    count.textContent = col.length;

    if (!col.length) {
      el.innerHTML = `<div class="empty-state" style="padding:30px 12px;"><div class="empty-desc">Glissez des tâches ici</div></div>`;
      return;
    }
    el.innerHTML = col.map(t => taskCardHTML(t)).join('');
  });
}

function taskCardHTML(t) {
  return `
  <div class="task-card" draggable="true"
    ondragstart="onDragStart(event, ${t.id})"
    ondragend="onDragEnd(event)">
    <div class="task-ai-score">${t.ai_score ? 'AI #' + t.ai_score : ''}</div>
    <div class="task-title">${escHtml(t.title)}</div>
    ${t.description ? `<div style="font-size:12px;color:var(--text-muted);margin-bottom:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${escHtml(t.description)}</div>` : ''}
    <div class="task-meta">
      <span class="badge badge-${t.priority}">${priorityLabel(t.priority)}</span>
      <div style="margin-left:auto; display:flex; gap:6px;">
        <button class="btn btn-ghost btn-icon btn-sm" onclick="editTask(${t.id})" title="Modifier" style="padding:4px 6px; font-size:12px;">✏️</button>
        <button class="btn btn-danger btn-icon btn-sm" onclick="deleteTask(${t.id})" title="Supprimer" style="padding:4px 6px; font-size:12px;">🗑️</button>
      </div>
    </div>
  </div>`;
}

function filterKanban(prio, btn) {
  currentFilter = prio;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  renderKanban();
}

function filterTasks() {
  const q = document.getElementById('search-input').value.toLowerCase();
  // Only filter if kanban is visible
  const kanban = document.getElementById('view-kanban');
  if (kanban.style.display !== 'none') {
    const allCards = document.querySelectorAll('.task-card');
    allCards.forEach(card => {
      const title = card.querySelector('.task-title').textContent.toLowerCase();
      card.style.display = title.includes(q) ? '' : 'none';
    });
  }
}

/* ─────────────────────────────
   DRAG & DROP
───────────────────────────── */
function onDragStart(e, id) {
  draggedId = id;
  e.currentTarget.classList.add('dragging');
  e.dataTransfer.effectAllowed = 'move';
}

function onDragEnd(e) {
  e.currentTarget.classList.remove('dragging');
}

function onDragOver(e) {
  e.preventDefault();
  e.dataTransfer.dropEffect = 'move';
  e.currentTarget.style.background = 'rgba(99,102,241,0.05)';
}

function onDrop(e, status) {
  e.preventDefault();
  e.currentTarget.style.background = '';
  if (draggedId !== null) {
    updateTaskStatus(draggedId, status);
    draggedId = null;
  }
}

/* ─────────────────────────────
   ANALYTICS
───────────────────────────── */
let chartP, chartS;

function renderAnalytics() {
  const total    = tasks.length;
  const done     = tasks.filter(t => t.status === 'done').length;
  const pct      = total > 0 ? Math.round((done / total) * 100) + '%' : '—';
  const velocity = total > 0 ? (done / Math.max(1, 4)).toFixed(1) : '—';

  document.getElementById('ana-velocity').textContent   = velocity;
  document.getElementById('ana-completion').textContent = pct;
  document.getElementById('ana-ai').textContent         = tasks.filter(t => t.ai_score).length;

  const colors = { bg: ['rgba(244,63,94,0.6)','rgba(245,158,11,0.6)','rgba(99,102,241,0.6)'], border: ['#f43f5e','#f59e0b','#6366f1'] };

  const prioData = { labels: ['Haute','Moyenne','Basse'], datasets: [{ data: ['high','medium','low'].map(p => tasks.filter(t => t.priority===p).length), backgroundColor: colors.bg, borderColor: colors.border, borderWidth: 1.5 }] };
  const statData = { labels: ['À faire','En cours','Terminé'], datasets: [{ data: ['todo','inprogress','done'].map(s => tasks.filter(t => t.status===s).length), backgroundColor: ['rgba(99,102,241,0.5)','rgba(245,158,11,0.5)','rgba(16,185,129,0.5)'], borderColor: ['#6366f1','#f59e0b','#10b981'], borderWidth: 1.5 }] };

  const opts = { responsive: true, plugins: { legend: { labels: { color: '#94a3b8', font: { size: 12 } } } } };

  if (chartP) chartP.destroy();
  if (chartS) chartS.destroy();
  chartP = new Chart(document.getElementById('chart-priority'), { type: 'doughnut', data: prioData, options: opts });
  chartS = new Chart(document.getElementById('chart-status'),   { type: 'doughnut', data: statData, options: opts });
}

/* ─────────────────────────────
   AI
───────────────────────────── */
async function runAIPrioritize() {
  const btn = document.getElementById('ai-btn-content');
  btn.innerHTML = '<div class="spinner" style="display:inline-block;"></div> Analyse en cours...';

  try {
    const res = await apiFetch('/ai/prioritize', { method: 'POST', body: JSON.stringify({ tasks: tasks.map(t => t.title) }) });
    document.getElementById('ai-quick-text').textContent = res?.result || JSON.stringify(res);
    document.getElementById('ai-quick-result').style.display = '';
    toast('Analyse IA terminée !', 'success');
  } catch {
    document.getElementById('ai-quick-text').textContent = '⚠️ Backend non connecté. Lancez le serveur FastAPI pour utiliser l\'IA.';
    document.getElementById('ai-quick-result').style.display = '';
  }
  btn.innerHTML = '⚡ Analyser le backlog';
}

async function runAIFull() {
  const btn      = document.getElementById('ai-full-btn');
  const context  = document.getElementById('ai-context').value;
  const criteria = document.getElementById('ai-criteria').value;
  btn.disabled = true;
  btn.innerHTML = '<div class="spinner" style="display:inline-block;"></div> Analyse en cours...';

  const prompt = tasks.map((t, i) => `${i+1}. [${t.priority.toUpperCase()}] ${t.title} — ${t.description || 'sans description'}`).join('\n');

  try {
    const res = await apiFetch('/ai/prioritize', {
      method: 'POST',
      body: JSON.stringify({ tasks: prompt, context, criteria })
    });
    document.getElementById('ai-full-text').textContent = res?.result || JSON.stringify(res);
    document.getElementById('ai-full-result').style.display = '';
    toast('Analyse complète terminée !', 'success');
  } catch {
    document.getElementById('ai-full-text').textContent = `⚠️ Backend non connecté.\n\nVos tâches :\n${prompt}\n\nLancez le serveur FastAPI (cd Backend && py -m uvicorn main:app --reload) pour obtenir l'analyse GPT-4o.`;
    document.getElementById('ai-full-result').style.display = '';
  }
  btn.disabled = false;
  btn.innerHTML = '⚡ Lancer l\'analyse IA complète';
}

/* ─────────────────────────────
   MODAL
───────────────────────────── */
function openModal(name) {
  if (name === 'new-task') {
    document.getElementById('edit-task-id').value           = '';
    document.getElementById('task-title-input').value      = '';
    document.getElementById('task-desc-input').value       = '';
    document.getElementById('task-priority-input').value   = 'medium';
    document.getElementById('task-status-input').value     = 'todo';
    document.getElementById('modal-task-title').textContent = 'Nouvelle tâche';
  }
  document.getElementById('modal-' + name).classList.add('open');
  setTimeout(() => document.getElementById('task-title-input')?.focus(), 50);
}

function closeModal(name) {
  document.getElementById('modal-' + name).classList.remove('open');
}

function closeModalOutside(e) {
  if (e.target === e.currentTarget) closeModal(e.currentTarget.id.replace('modal-', ''));
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
});

/* ─────────────────────────────
   TOAST
───────────────────────────── */
function toast(msg, type = 'info') {
  const icon = { success: '✓', error: '✕', info: 'ℹ' }[type] || 'ℹ';
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span style="font-weight:600;">${icon}</span> ${msg}`;
  document.getElementById('toasts').appendChild(el);
  requestAnimationFrame(() => { el.offsetHeight; el.classList.add('show'); });
  setTimeout(() => { el.classList.remove('show'); setTimeout(() => el.remove(), 400); }, 3000);
}

/* ─────────────────────────────
   HELPERS
───────────────────────────── */
const priorityLabel = p => ({ high: '🔴 Haute', medium: '🟡 Moyenne', low: '🟢 Basse' }[p] || p);
const statusLabel   = s => ({ todo: 'À faire', inprogress: 'En cours', done: 'Terminé' }[s] || s);
const escHtml = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');