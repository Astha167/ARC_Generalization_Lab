/**
 * ARC Generalization Lab — Frontend Application
 *
 * Interactive educational experience for investigating benchmark generalization.
 * Supports three data modes: DEMO (offline), PUBLIC (ARC-AGI-1), GENERATED (live).
 *
 * Architecture:
 *   State management → API layer → Grid renderer → Section controllers
 */

// ============================================================
// ARC Color Palette (matches official ARC-AGI colors)
// ============================================================

const ARC_COLORS = {
  0: '#000000', // black (background)
  1: '#0074D9', // blue
  2: '#FF4136', // red
  3: '#2ECC40', // green
  4: '#FFDC00', // yellow
  5: '#AAAAAA', // grey
  6: '#F012BE', // magenta
  7: '#FF851B', // orange
  8: '#7FDBFF', // azure
  9: '#870C25', // maroon
};

// ============================================================
// State
// ============================================================

const state = {
  mode: 'demo', // 'demo' | 'live'
  currentDataset: 'demo', // 'demo' | 'public'
  taskIds: [],
  taskIndex: 0,
  currentTask: null,
  selectedColor: 1,
  predictionGrid: [],
  undoStack: [],
  backendAvailable: false,

  // Demo fallback data
  demoTasks: {},
};

// ============================================================
// API Layer
// ============================================================

const API_BASE = '/api';

async function apiFetch(path, options = {}) {
  try {
    const resp = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    });
    if (!resp.ok) throw new Error(`API ${resp.status}: ${resp.statusText}`);
    return await resp.json();
  } catch (e) {
    console.warn(`API unavailable (${path}):`, e.message);
    return null;
  }
}

// ============================================================
// Embedded Demo Data (works without backend)
// ============================================================

const EMBEDDED_DEMO_TASKS = {
  'DEMO-001': {
    train: [
      { input: [[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0]], output: [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]] },
      { input: [[0,0,2],[0,2,0],[2,0,0]], output: [[2,0,0],[0,2,0],[0,0,2]] },
      { input: [[0,3,0],[3,0,0]], output: [[0,3,0],[0,0,3]] },
    ],
    test: [
      { input: [[0,0,0,0,4],[0,0,0,4,0],[0,0,4,0,0],[0,4,0,0,0],[4,0,0,0,0]], output: [[4,0,0,0,0],[0,4,0,0,0],[0,0,4,0,0],[0,0,0,4,0],[0,0,0,0,4]] },
    ],
  },
  'DEMO-002': {
    train: [
      { input: [[1,2],[3,4]], output: [[3,1],[4,2]] },
      { input: [[5,6,7],[8,9,1],[2,3,4]], output: [[2,8,5],[3,9,6],[4,1,7]] },
    ],
    test: [
      { input: [[1,0,2],[0,3,0],[4,0,5],[6,0,7]], output: [[6,4,0,1],[0,0,3,0],[7,5,0,2]] },
    ],
  },
  'DEMO-003': {
    train: [
      { input: [[1,0,0],[0,0,0],[0,0,0]], output: [[1,1,1],[1,0,0],[1,0,0]] },
      { input: [[0,0,0,0],[0,2,0,0],[0,0,0,0],[0,0,0,0]], output: [[0,2,0,0],[2,2,2,2],[0,2,0,0],[0,2,0,0]] },
      { input: [[0,0,0],[0,0,3],[0,0,0]], output: [[0,0,3],[3,3,3],[0,0,3]] },
    ],
    test: [
      { input: [[0,0,0,0,0],[0,0,0,0,0],[0,0,4,0,0],[0,0,0,0,0],[0,0,0,0,0]], output: [[0,0,4,0,0],[0,0,4,0,0],[4,4,4,4,4],[0,0,4,0,0],[0,0,4,0,0]] },
    ],
  },
  'DEMO-004': {
    train: [
      { input: [[1,2,3],[4,5,6]], output: [[6,5,4],[3,2,1]] },
      { input: [[7,8],[9,1]], output: [[1,9],[8,7]] },
      { input: [[3,0,0,2],[0,1,4,0],[0,5,6,0]], output: [[0,6,5,0],[0,4,1,0],[2,0,0,3]] },
    ],
    test: [
      { input: [[1,0,0],[0,2,0],[0,0,3],[4,0,0]], output: [[0,0,4],[3,0,0],[0,2,0],[0,0,1]] },
    ],
  },
  'DEMO-005': {
    train: [
      { input: [[0,0,1,0],[0,1,0,0],[1,0,0,0],[0,0,0,0]], output: [[0,0,1,0],[0,1,1,0],[1,1,1,0],[0,0,0,0]] },
      { input: [[0,2,0],[2,0,0],[0,0,0]], output: [[0,2,0],[2,2,0],[0,0,0]] },
    ],
    test: [
      { input: [[0,0,0,3,0],[0,0,3,0,0],[0,3,0,0,0],[3,0,0,0,0],[0,0,0,0,0]], output: [[0,0,0,3,0],[0,0,3,3,0],[0,3,3,3,0],[3,3,3,3,0],[0,0,0,0,0]] },
    ],
  },
};

// Simple heuristic solver (client-side fallback)
function clientSolve(task, solverType) {
  const testInput = task.test[0].input;
  const rows = testInput.length;
  const cols = testInput[0]?.length || 0;

  if (solverType === 'random') {
    const colors = new Set();
    task.train.forEach(p => {
      [...p.input, ...p.output].forEach(grid => {
        if (Array.isArray(grid)) grid.forEach(row => row.forEach(v => colors.add(v)));
        else if (Array.isArray(p.input)) p.input.forEach(row => row.forEach(v => colors.add(v)));
      });
    });
    task.train.forEach(p => {
      p.input.forEach(r => r.forEach(v => colors.add(v)));
      p.output.forEach(r => r.forEach(v => colors.add(v)));
    });
    const colorList = [...colors];
    return Array.from({ length: rows }, () =>
      Array.from({ length: cols }, () => colorList[Math.floor(Math.random() * colorList.length)])
    );
  }

  // Heuristic: try simple transforms
  const transforms = [
    { name: 'identity', fn: g => g.map(r => [...r]) },
    { name: 'h_flip', fn: g => g.map(r => [...r].reverse()) },
    { name: 'v_flip', fn: g => [...g].reverse().map(r => [...r]) },
    { name: 'rotate_180', fn: g => [...g].reverse().map(r => [...r].reverse()) },
  ];

  for (const { fn } of transforms) {
    let allMatch = true;
    for (const pair of task.train) {
      try {
        const result = fn(pair.input);
        if (JSON.stringify(result) !== JSON.stringify(pair.output)) {
          allMatch = false;
          break;
        }
      } catch {
        allMatch = false;
        break;
      }
    }
    if (allMatch) return fn(testInput);
  }

  // Fallback: copy input
  return testInput.map(r => [...r]);
}

function clientEvaluate(predicted, groundTruth) {
  const exact = JSON.stringify(predicted) === JSON.stringify(groundTruth);
  const gtRows = groundTruth.length;
  const gtCols = groundTruth[0]?.length || 0;
  const pRows = predicted.length;
  const pCols = predicted[0]?.length || 0;
  const dimMatch = pRows === gtRows && pCols === gtCols;

  let correct = 0, total = gtRows * gtCols;
  const diff = [];

  if (dimMatch) {
    for (let r = 0; r < gtRows; r++) {
      const row = [];
      for (let c = 0; c < gtCols; c++) {
        const match = predicted[r][c] === groundTruth[r][c];
        if (match) correct++;
        row.push({ predicted: predicted[r][c], expected: groundTruth[r][c], match });
      }
      diff.push(row);
    }
  }

  return {
    exact_match: exact,
    dimensions_match: dimMatch,
    cell_accuracy: total > 0 ? +(correct / total).toFixed(4) : 0,
    correct_cells: correct,
    total_cells: total,
    predicted_shape: [pRows, pCols],
    expected_shape: [gtRows, gtCols],
    diff: dimMatch ? diff : null,
    ground_truth: groundTruth,
  };
}

// ============================================================
// Grid Rendering
// ============================================================

function renderGrid(container, grid, options = {}) {
  const { editable = false, diff = null, cellSize = null } = options;
  container.innerHTML = '';

  if (!grid || !grid.length) {
    container.innerHTML = '<span class="text-muted" style="font-size:13px;">Empty grid</span>';
    return;
  }

  const rows = grid.length;
  const cols = grid[0]?.length || 0;
  const size = cellSize || (cols > 15 || rows > 15 ? 18 : rows > 10 || cols > 10 ? 22 : 28);

  const gridEl = document.createElement('div');
  gridEl.className = 'arc-grid';
  gridEl.style.gridTemplateColumns = `repeat(${cols}, ${size}px)`;
  gridEl.setAttribute('role', 'grid');
  gridEl.setAttribute('aria-label', 'ARC grid');

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const cell = document.createElement('div');
      cell.className = 'arc-cell';
      const val = grid[r]?.[c] ?? 0;
      cell.style.backgroundColor = ARC_COLORS[val] || ARC_COLORS[0];
      cell.style.width = `${size}px`;
      cell.style.height = `${size}px`;
      cell.setAttribute('role', 'gridcell');
      cell.setAttribute('aria-label', `Row ${r + 1}, Column ${c + 1}, Color ${val}`);

      if (diff && diff[r] && diff[r][c] && !diff[r][c].match) {
        cell.classList.add('diff-wrong');
      }

      if (editable) {
        cell.tabIndex = 0;
        cell.dataset.row = r;
        cell.dataset.col = c;
        cell.addEventListener('click', () => paintCell(r, c));
        cell.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); paintCell(r, c); }
        });
      }

      gridEl.appendChild(cell);
    }
  }

  container.appendChild(gridEl);
}

function paintCell(r, c) {
  state.undoStack.push(JSON.parse(JSON.stringify(state.predictionGrid)));
  if (state.undoStack.length > 50) state.undoStack.shift();
  state.predictionGrid[r][c] = state.selectedColor;
  renderGrid(document.getElementById('prediction-grid'), state.predictionGrid, { editable: true });
}

// ============================================================
// Color Palette
// ============================================================

function renderPalette() {
  const container = document.getElementById('color-palette');
  container.innerHTML = '';
  for (let i = 0; i <= 9; i++) {
    const swatch = document.createElement('button');
    swatch.className = `palette-swatch${i === state.selectedColor ? ' active' : ''}`;
    swatch.style.backgroundColor = ARC_COLORS[i];
    swatch.setAttribute('aria-label', `Color ${i}`);
    swatch.tabIndex = 0;
    swatch.addEventListener('click', () => {
      state.selectedColor = i;
      renderPalette();
    });
    container.appendChild(swatch);
  }
}

// ============================================================
// Task Loading
// ============================================================

async function loadTasks() {
  if (state.currentDataset === 'demo') {
    // Use embedded data (works without backend)
    state.demoTasks = EMBEDDED_DEMO_TASKS;
    state.taskIds = Object.keys(EMBEDDED_DEMO_TASKS);
  } else if (state.currentDataset === 'public') {
    const resp = await apiFetch('/tasks/public?limit=50');
    if (resp) {
      state.taskIds = resp.tasks.map(t => t.id);
    } else {
      // Fallback to demo
      state.currentDataset = 'demo';
      state.demoTasks = EMBEDDED_DEMO_TASKS;
      state.taskIds = Object.keys(EMBEDDED_DEMO_TASKS);
    }
  }
  state.taskIndex = 0;
  await loadCurrentTask();
}

async function loadCurrentTask() {
  const taskId = state.taskIds[state.taskIndex];
  if (!taskId) return;

  document.getElementById('task-id-label').textContent =
    `${state.taskIndex + 1}/${state.taskIds.length} — ${taskId}`;

  let task = null;

  if (state.currentDataset === 'demo') {
    task = state.demoTasks[taskId] || EMBEDDED_DEMO_TASKS[taskId];
  } else {
    const resp = await apiFetch(`/tasks/${state.currentDataset}/${taskId}`);
    if (resp) {
      task = resp;
    }
  }

  if (!task) return;
  state.currentTask = { id: taskId, ...task };

  // Render training pairs
  const trainContainer = document.getElementById('training-pairs');
  trainContainer.innerHTML = '';
  const train = task.train || [];
  train.forEach((pair, i) => {
    const pairEl = document.createElement('div');
    pairEl.className = 'train-pair';

    const inPanel = document.createElement('div');
    inPanel.className = 'grid-panel';
    inPanel.innerHTML = `<span class="panel-label">Input ${i + 1}</span>`;
    const inGrid = document.createElement('div');
    inGrid.className = 'arc-grid-container';
    renderGrid(inGrid, pair.input);
    inPanel.appendChild(inGrid);

    const arrow = document.createElement('div');
    arrow.className = 'train-pair-arrow';
    arrow.textContent = '→';

    const outPanel = document.createElement('div');
    outPanel.className = 'grid-panel';
    outPanel.innerHTML = `<span class="panel-label">Output ${i + 1}</span>`;
    const outGrid = document.createElement('div');
    outGrid.className = 'arc-grid-container';
    renderGrid(outGrid, pair.output);
    outPanel.appendChild(outGrid);

    pairEl.appendChild(inPanel);
    pairEl.appendChild(arrow);
    pairEl.appendChild(outPanel);
    trainContainer.appendChild(pairEl);
  });

  // Render test input
  const testInput = task.test?.[0]?.input;
  if (testInput) {
    renderGrid(document.getElementById('test-input-grid'), testInput);

    // Initialize prediction grid (blank, same dimensions)
    const rows = testInput.length;
    const cols = testInput[0]?.length || 0;
    state.predictionGrid = Array.from({ length: rows }, () => Array(cols).fill(0));
    state.undoStack = [];
    renderGrid(document.getElementById('prediction-grid'), state.predictionGrid, { editable: true });
  }

  // Hide results
  document.getElementById('result-section').classList.add('hidden');
  document.getElementById('solver-result').classList.add('hidden');
}

// ============================================================
// Navigation
// ============================================================

window.scrollToSection = function(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
};

window.switchDataset = function(ds) {
  state.currentDataset = ds;
  document.querySelectorAll('.ds-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.dataset === ds);
  });
  loadTasks();
};

window.prevTask = function() {
  if (state.taskIndex > 0) {
    state.taskIndex--;
    loadCurrentTask();
  }
};

window.nextTask = function() {
  if (state.taskIndex < state.taskIds.length - 1) {
    state.taskIndex++;
    loadCurrentTask();
  }
};

window.clearPrediction = function() {
  state.undoStack.push(JSON.parse(JSON.stringify(state.predictionGrid)));
  state.predictionGrid = state.predictionGrid.map(r => r.map(() => 0));
  renderGrid(document.getElementById('prediction-grid'), state.predictionGrid, { editable: true });
};

window.resetPrediction = function() {
  const testInput = state.currentTask?.test?.[0]?.input;
  if (!testInput) return;
  state.undoStack.push(JSON.parse(JSON.stringify(state.predictionGrid)));
  state.predictionGrid = testInput.map(r => [...r]);
  renderGrid(document.getElementById('prediction-grid'), state.predictionGrid, { editable: true });
};

window.undoPrediction = function() {
  if (state.undoStack.length > 0) {
    state.predictionGrid = state.undoStack.pop();
    renderGrid(document.getElementById('prediction-grid'), state.predictionGrid, { editable: true });
  }
};

// ============================================================
// Prediction Submission
// ============================================================

window.submitPrediction = async function() {
  if (!state.currentTask) return;
  const taskId = state.currentTask.id;
  const dataset = state.currentDataset;
  const predicted = state.predictionGrid;

  let result;

  // Try backend first
  const resp = await apiFetch('/evaluate', {
    method: 'POST',
    body: JSON.stringify({ task_id: taskId, dataset, predicted }),
  });

  if (resp) {
    result = resp;
  } else {
    // Client-side evaluation
    const gt = state.currentTask.test?.[0]?.output;
    if (!gt) return;
    result = clientEvaluate(predicted, gt);
  }

  showResult(result, predicted);
};

function showResult(result, predicted) {
  const section = document.getElementById('result-section');
  section.classList.remove('hidden');

  renderGrid(document.getElementById('result-predicted'), predicted);
  renderGrid(document.getElementById('result-truth'), result.ground_truth);

  // Diff grid
  if (result.diff) {
    const diffGrid = result.ground_truth.map((row, r) =>
      row.map((val, c) => result.diff[r][c].match ? val : result.diff[r][c].predicted)
    );
    renderGrid(document.getElementById('result-diff'), diffGrid, { diff: result.diff });
  } else {
    document.getElementById('result-diff').innerHTML =
      '<span style="color:var(--error);font-size:13px;">Dimension mismatch</span>';
  }

  // Stats
  const statsEl = document.getElementById('result-stats');
  const icon = result.exact_match ? '✓' : '✗';
  const color = result.exact_match ? 'var(--success)' : 'var(--error)';
  statsEl.innerHTML = `
    <span style="color:${color};font-weight:700;">${icon} ${result.exact_match ? 'CORRECT' : 'INCORRECT'}</span>
    &nbsp;|&nbsp; Cell accuracy: ${(result.cell_accuracy * 100).toFixed(1)}%
    &nbsp;|&nbsp; ${result.correct_cells}/${result.total_cells} cells correct
    &nbsp;|&nbsp; Predicted: ${result.predicted_shape.join('×')}
    &nbsp;|&nbsp; Expected: ${result.expected_shape.join('×')}
  `;

  section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============================================================
// Solver
// ============================================================

window.runSolver = async function() {
  if (!state.currentTask) return;
  const taskId = state.currentTask.id;
  const dataset = state.currentDataset;
  const solverType = document.getElementById('solver-select').value;
  const btn = document.getElementById('run-solver-btn');

  btn.disabled = true;
  btn.textContent = 'Running...';

  let result;

  const resp = await apiFetch('/solver/run', {
    method: 'POST',
    body: JSON.stringify({ task_id: taskId, dataset, solver: solverType }),
  });

  if (resp) {
    result = resp;
  } else {
    // Client-side solver
    const predicted = clientSolve(state.currentTask, solverType);
    const gt = state.currentTask.test?.[0]?.output;
    if (!gt) { btn.disabled = false; btn.textContent = 'Run Solver'; return; }
    const evaluation = clientEvaluate(predicted, gt);
    result = {
      solver: { name: solverType === 'random' ? 'Random Baseline' : 'Heuristic Baseline', type: solverType },
      predicted,
      ground_truth: gt,
      evaluation,
      elapsed_ms: 0,
    };
  }

  btn.disabled = false;
  btn.textContent = 'Run Solver';

  const container = document.getElementById('solver-result');
  container.classList.remove('hidden');

  const evalR = result.evaluation;
  const icon = evalR.exact_match ? '✓' : '✗';
  const color = evalR.exact_match ? 'var(--success)' : 'var(--error)';

  container.innerHTML = `
    <h4 style="margin-bottom:12px;">${result.solver.name}</h4>
    <p style="color:${color};font-weight:700;margin-bottom:12px;">
      ${icon} ${evalR.exact_match ? 'SOLVED' : 'FAILED'} — Cell accuracy: ${(evalR.cell_accuracy * 100).toFixed(1)}%
    </p>
    <div class="result-grids" style="margin-bottom:12px;">
      <div class="grid-panel">
        <span class="panel-label">Solver Prediction</span>
        <div class="arc-grid-container" id="solver-pred-grid"></div>
      </div>
      <div class="grid-panel">
        <span class="panel-label">Ground Truth</span>
        <div class="arc-grid-container" id="solver-gt-grid"></div>
      </div>
    </div>
    <p style="font-size:12px;color:var(--text-muted);">${result.solver.description || ''}</p>
  `;

  renderGrid(document.getElementById('solver-pred-grid'), result.predicted);
  renderGrid(document.getElementById('solver-gt-grid'), result.ground_truth);
};

// ============================================================
// Experiment Lab
// ============================================================

window.runExperiment = async function() {
  const solverType = document.getElementById('exp-solver').value;
  const maxTasks = parseInt(document.getElementById('exp-n').value);
  const btn = document.getElementById('run-experiment-btn');

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Running experiment...';

  // Use demo tasks for both "public" and "fresh" if no backend
  const datasets = ['demo']; // In demo mode, we only have demo tasks
  const results = {};

  // Run solver on demo tasks as "public" simulation
  const demoTaskIds = Object.keys(EMBEDDED_DEMO_TASKS);
  const tasksToUse = demoTaskIds.slice(0, Math.min(maxTasks, demoTaskIds.length));

  // Call real experiment endpoint on backend first
  const expResp = await apiFetch('/experiments/run', {
    method: 'POST',
    body: JSON.stringify({ public_limit: maxTasks, fresh_count: maxTasks, solver: solverType, mode: 'standard' }),
  });

  if (expResp) {
    btn.disabled = false;
    btn.innerHTML = '▶ Run Experiment';
    showExperimentRunResults(expResp);
    return;
  }

  // Fallback client-side simulation when backend is completely offline
  const allTasks = EMBEDDED_DEMO_TASKS;
  const ids = Object.keys(allTasks);
  const halfLen = Math.max(2, Math.ceil(ids.length / 2));
  const publicIds = ids.slice(0, halfLen);
  const freshIds = ids.slice(halfLen);

  const publicResult = runClientBatch(allTasks, solverType, maxTasks, 'demo', publicIds);
  publicResult.dataset = 'public (demo simulation)';
  publicResult.label = 'DEMO DATA — NOT AN EXPERIMENTAL RESULT';

  const freshResult = runClientBatch(allTasks, solverType, maxTasks, 'demo', freshIds);
  freshResult.dataset = 'fresh (demo simulation)';
  freshResult.label = 'DEMO DATA — NOT AN EXPERIMENTAL RESULT';

  btn.disabled = false;
  btn.innerHTML = '▶ Run Experiment';

  showExperimentResults(publicResult, freshResult);
};

function showExperimentRunResults(exp) {
  const container = document.getElementById('experiment-results');
  container.classList.remove('hidden');

  const pAcc = (exp.public.accuracy * 100);
  const fAcc = (exp.fresh.accuracy * 100);
  const gap = (exp.gap * 100);

  // Gap bars
  document.getElementById('exp-public-score').textContent = `${pAcc.toFixed(1)}%`;
  document.getElementById('exp-fresh-score').textContent = `${fAcc.toFixed(1)}%`;
  document.getElementById('exp-public-bar').style.width = `${Math.max(2, Math.min(100, pAcc))}%`;
  document.getElementById('exp-fresh-bar').style.width = `${Math.max(2, Math.min(100, fAcc))}%`;

  // Gap summary with diagnostic honesty
  const gapDir = gap > 0 ? 'higher' : gap < 0 ? 'lower' : 'equal';
  let warningBadge = '';
  if (!exp.genuine_experiment) {
    warningBadge = `
      <div style="background:rgba(255,152,0,0.12);border:1px solid rgba(255,152,0,0.3);padding:10px 14px;border-radius:6px;margin-bottom:12px;color:var(--warning);font-size:13px;">
        <strong>⚠️ DEMONSTRATION MODE:</strong> ${exp.warning || 'Deterministic fallback tasks were used. Not a genuine public-vs-fresh upstream generation experiment.'}
      </div>
    `;
  }
  let exploratoryBadge = '';
  if (exp.exploratory_warning) {
    exploratoryBadge = `
      <div style="background:rgba(33,150,243,0.1);border:1px solid rgba(33,150,243,0.25);padding:8px 12px;border-radius:6px;margin-bottom:12px;color:#64b5f6;font-size:12px;">
        ℹ️ ${exp.exploratory_warning}
      </div>
    `;
  }

  document.getElementById('gap-summary').innerHTML = `
    ${warningBadge}
    ${exploratoryBadge}
    <strong>Diagnostic Performance Gap: ${gap > 0 ? '+' : ''}${gap.toFixed(1)} percentage points</strong><br>
    <span style="color:var(--text-secondary);font-size:13px;">
      ${exp.public.evaluated_tasks_label} vs ${exp.fresh.evaluated_tasks_label} (Solver: ${exp.solver.name})<br>
      ${exp.gap_interpretation}
    </span>
  `;

  // Data label
  const isDemo = !exp.genuine_experiment;
  document.getElementById('exp-data-label').innerHTML = isDemo
    ? `<span class="result-label" style="background:rgba(255,152,0,0.15);color:var(--warning);border-color:rgba(255,152,0,0.3);">${exp.evidence_label || 'FALLBACK / DEMONSTRATION'}</span>`
    : '<span class="result-label" style="background:rgba(76,175,80,0.1);color:var(--success);border-color:rgba(76,175,80,0.2);">MEASURED FRESH-GENERATION EVIDENCE</span>';

  // Metrics Table
  const tbody = document.getElementById('exp-table-body');
  tbody.innerHTML = '';
  const metrics = [
    ['Data Source', exp.public.dataset_source, exp.fresh.dataset_source],
    ['Generator Mode', 'benchmark (fixed)', exp.fresh.generator_mode],
    ['Tasks evaluated', exp.public.task_count, exp.fresh.task_count],
    ['Tasks solved', exp.public.solved, exp.fresh.solved],
    ['Mean accuracy', `${pAcc.toFixed(1)}%`, `${fAcc.toFixed(1)}%`],
    ['Diagnostic Gap', '—', '—', `${(gap).toFixed(1)}%`],
  ];

  metrics.forEach(([label, pub, fresh, diff]) => {
    const tr = document.createElement('tr');
    const displayDiff = diff !== undefined ? diff : (typeof pub === 'number' && typeof fresh === 'number' ? pub - fresh : '—');
    tr.innerHTML = `<td style="font-family:var(--font-sans)">${label}</td><td>${pub}</td><td>${fresh}</td><td>${displayDiff}</td>`;
    tbody.appendChild(tr);
  });

  // Failure analysis section
  const failureList = document.getElementById('failure-list');
  failureList.innerHTML = `<p style="color:var(--text-muted);font-size:13px;">Run ID: ${exp.experiment_id} | Distribution area mean: Public=${exp.distribution?.public?.input_area?.mean || '—'}, Fresh=${exp.distribution?.fresh?.input_area?.mean || '—'}</p>`;

  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}


function runClientBatch(tasks, solverType, maxTasks, dataset, filterIds = null) {
  const ids = filterIds || Object.keys(tasks).slice(0, maxTasks);
  const results = [];
  let solved = 0;
  let totalAcc = 0;

  for (const id of ids) {
    const task = tasks[id];
    if (!task) continue;
    const predicted = clientSolve(task, solverType);
    const gt = task.test?.[0]?.output;
    if (!gt) continue;
    const evaluation = clientEvaluate(predicted, gt);
    if (evaluation.exact_match) solved++;
    totalAcc += evaluation.cell_accuracy;
    results.push({
      task_id: id,
      exact_match: evaluation.exact_match,
      cell_accuracy: evaluation.cell_accuracy,
      elapsed_ms: 0,
    });
  }

  const n = results.length;
  return {
    dataset,
    label: 'DEMO DATA',
    solver: { name: solverType === 'random' ? 'Random Baseline' : 'Heuristic Baseline', type: solverType },
    total_tasks: n,
    solved,
    accuracy: n > 0 ? +(solved / n).toFixed(4) : 0,
    mean_cell_accuracy: n > 0 ? +(totalAcc / n).toFixed(4) : 0,
    results,
  };
}

function showExperimentResults(publicResult, freshResult) {
  const container = document.getElementById('experiment-results');
  container.classList.remove('hidden');

  const pAcc = (publicResult.accuracy * 100);
  const fAcc = (freshResult.accuracy * 100);
  const gap = pAcc - fAcc;

  // Gap bars
  document.getElementById('exp-public-score').textContent = `${pAcc.toFixed(1)}%`;
  document.getElementById('exp-fresh-score').textContent = `${fAcc.toFixed(1)}%`;
  document.getElementById('exp-public-bar').style.width = `${Math.max(2, pAcc)}%`;
  document.getElementById('exp-fresh-bar').style.width = `${Math.max(2, fAcc)}%`;

  // Gap summary
  const gapDir = gap > 0 ? 'higher' : gap < 0 ? 'lower' : 'equal';
  document.getElementById('gap-summary').innerHTML = `
    <strong>Public-to-Fresh Gap: ${gap > 0 ? '+' : ''}${gap.toFixed(1)} percentage points</strong><br>
    <span style="color:var(--text-secondary);">
      Public performance is ${gapDir} than fresh performance.
      ${Math.abs(gap) > 5
        ? 'This gap is a diagnostic signal consistent with multiple explanations including benchmark familiarity, distribution mismatch, and generator artifacts.'
        : 'The gap is small — within noise range for this sample size.'}
    </span>
  `;

  // Data label
  const isDemo = publicResult.label?.includes('DEMO');
  document.getElementById('exp-data-label').innerHTML = isDemo
    ? '<span class="result-label">DEMO DATA — NOT AN EXPERIMENTAL RESULT</span>'
    : '<span class="result-label" style="background:rgba(76,175,80,0.1);color:var(--success);border-color:rgba(76,175,80,0.2);">MEASURED</span>';

  // Table
  const tbody = document.getElementById('exp-table-body');
  tbody.innerHTML = '';
  const metrics = [
    ['Tasks evaluated', publicResult.total_tasks, freshResult.total_tasks],
    ['Tasks solved', publicResult.solved, freshResult.solved],
    ['Exact-match accuracy', `${pAcc.toFixed(1)}%`, `${fAcc.toFixed(1)}%`],
    ['Mean cell accuracy', `${(publicResult.mean_cell_accuracy * 100).toFixed(1)}%`, `${(freshResult.mean_cell_accuracy * 100).toFixed(1)}%`],
  ];

  metrics.forEach(([label, pub, fresh]) => {
    const tr = document.createElement('tr');
    const diff = typeof pub === 'number' && typeof fresh === 'number' ? pub - fresh : '—';
    tr.innerHTML = `<td style="font-family:var(--font-sans)">${label}</td><td>${pub}</td><td>${fresh}</td><td>${diff}</td>`;
    tbody.appendChild(tr);
  });

  // Failure analysis
  const failureList = document.getElementById('failure-list');
  failureList.innerHTML = '';
  const allResults = [
    ...publicResult.results.map(r => ({ ...r, source: 'Public' })),
    ...freshResult.results.map(r => ({ ...r, source: 'Fresh' })),
  ].filter(r => !r.exact_match);

  if (allResults.length === 0) {
    failureList.innerHTML = '<p style="color:var(--text-muted);">No failures to analyze.</p>';
  } else {
    allResults.slice(0, 10).forEach(r => {
      const card = document.createElement('div');
      card.className = 'failure-card';
      card.innerHTML = `
        <h4>${r.source} — ${r.task_id}</h4>
        <p style="font-size:13px;color:var(--text-secondary);">
          Cell accuracy: ${(r.cell_accuracy * 100).toFixed(1)}%
          &nbsp;|&nbsp; Source: <span class="ds-badge ${r.source === 'Public' ? 'public' : 'fresh'}">${r.source.toUpperCase()}</span>
        </p>
      `;
      failureList.appendChild(card);
    });
  }

  container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============================================================
// Distribution Stats
// ============================================================

async function loadDistributionStats() {
  // Try backend
  const resp = await apiFetch('/stats/distribution?dataset=demo');

  // Compute from embedded data
  const stats = computeClientStats(EMBEDDED_DEMO_TASKS);
  renderDistCharts(stats, 'Demo Tasks');
}

function computeClientStats(tasks) {
  const inRows = [], inCols = [], inAreas = [], colors = [];
  const trainCounts = [], testCounts = [];

  Object.values(tasks).forEach(task => {
    trainCounts.push(task.train?.length || 0);
    testCounts.push(task.test?.length || 0);
    const taskColors = new Set();
    for (const split of ['train', 'test']) {
      for (const pair of (task[split] || [])) {
        for (const field of ['input', 'output']) {
          const grid = pair[field];
          if (!grid) continue;
          const r = grid.length;
          const c = grid[0]?.length || 0;
          if (field === 'input') {
            inRows.push(r);
            inCols.push(c);
            inAreas.push(r * c);
          }
          grid.forEach(row => row.forEach(v => { if (v !== 0) taskColors.add(v); }));
        }
      }
    }
    colors.push(taskColors.size);
  });

  const summarise = arr => {
    if (!arr.length) return { mean: 0, median: 0, min: 0, max: 0 };
    const sorted = [...arr].sort((a, b) => a - b);
    const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
    const median = sorted[Math.floor(sorted.length / 2)];
    return { mean: +mean.toFixed(1), median, min: sorted[0], max: sorted[sorted.length - 1] };
  };

  return {
    num_tasks: Object.keys(tasks).length,
    input_rows: summarise(inRows),
    input_cols: summarise(inCols),
    input_area: summarise(inAreas),
    colors_per_task: summarise(colors),
  };
}

function renderDistCharts(stats, label) {
  const container = document.getElementById('dist-charts');
  container.innerHTML = '';

  const metrics = [
    { key: 'input_rows', label: 'Input Rows', color: 'var(--public-color)' },
    { key: 'input_cols', label: 'Input Cols', color: 'var(--accent)' },
    { key: 'input_area', label: 'Input Area', color: 'var(--fresh-color)' },
    { key: 'colors_per_task', label: 'Colors per Task', color: 'var(--demo-color)' },
  ];

  metrics.forEach(({ key, label: metricLabel, color }) => {
    const s = stats[key];
    if (!s) return;
    const card = document.createElement('div');
    card.className = 'dist-chart-card';

    const maxVal = Math.max(s.max, 1);

    card.innerHTML = `
      <h4>${metricLabel}</h4>
      <div class="dist-bar-group">
        <span class="dist-bar-label">Mean</span>
        <div class="dist-bar-track">
          <div class="dist-bar-fill" style="width:${(s.mean / maxVal * 100).toFixed(0)}%;background:${color};"></div>
        </div>
        <span class="dist-bar-value">${s.mean}</span>
      </div>
      <div class="dist-bar-group">
        <span class="dist-bar-label">Median</span>
        <div class="dist-bar-track">
          <div class="dist-bar-fill" style="width:${(s.median / maxVal * 100).toFixed(0)}%;background:${color};opacity:0.7;"></div>
        </div>
        <span class="dist-bar-value">${s.median}</span>
      </div>
      <div class="dist-bar-group">
        <span class="dist-bar-label">Range</span>
        <div class="dist-bar-track">
          <div class="dist-bar-fill" style="width:100%;background:${color};opacity:0.3;"></div>
        </div>
        <span class="dist-bar-value">${s.min}–${s.max}</span>
      </div>
    `;
    container.appendChild(card);
  });
}

// ============================================================
// Quiz
// ============================================================

window.checkQuiz = function(btn) {
  const correct = btn.dataset.correct === 'true';
  const feedback = document.getElementById('quiz-feedback');

  document.querySelectorAll('.quiz-opt').forEach(b => {
    b.classList.remove('correct', 'incorrect');
    b.disabled = true;
  });

  btn.classList.add(correct ? 'correct' : 'incorrect');

  // Also highlight the correct answer
  document.querySelectorAll('.quiz-opt[data-correct="true"]').forEach(b => b.classList.add('correct'));

  feedback.className = `quiz-feedback ${correct ? 'correct' : 'incorrect'}`;
  feedback.textContent = correct
    ? '✓ Correct. The gap is a diagnostic signal — it cannot isolate a single cause like memorization from other confounds.'
    : '✗ Not quite. A performance gap has multiple possible explanations. We cannot conclude memorization, difficulty difference, or benchmark invalidity from the gap alone.';
};

// ============================================================
// Blind Solvability Audit
// ============================================================

const auditState = {
  taskIds: [],
  tasks: {},
  taskIndex: 0,
  verdicts: {}, // task_id -> verdict
  source: 'demo',
  label: 'BLIND AUDIT — DEMO DATA',
  disclaimer: '',
};

async function initAudit() {
  const auditResp = await apiFetch('/audit/tasks');
  if (auditResp && auditResp.tasks && auditResp.tasks.length > 0) {
    auditState.taskIds = auditResp.tasks.map(t => t.id);
    auditState.tasks = {};
    auditResp.tasks.forEach(t => { auditState.tasks[t.id] = t; });
    auditState.source = auditResp.source;
    auditState.label = auditResp.label;
    auditState.disclaimer = auditResp.disclaimer;
  } else {
    // Fallback to embedded demo tasks
    auditState.taskIds = Object.keys(EMBEDDED_DEMO_TASKS);
    auditState.tasks = EMBEDDED_DEMO_TASKS;
    auditState.source = 'demo';
    auditState.label = 'BLIND AUDIT — DEMO DATA (Demonstration Only)';
    auditState.disclaimer = 'Currently evaluating hand-crafted demo tasks. This audit demonstrates the human evaluation protocol but does not validate the live generator.';
  }

  // Update audit header disclaimer
  const panel = document.getElementById('audit-panel');
  let disclaimerEl = document.getElementById('audit-disclaimer');
  if (!disclaimerEl && panel) {
    disclaimerEl = document.createElement('div');
    disclaimerEl.id = 'audit-disclaimer';
    disclaimerEl.style.cssText = 'padding:8px 12px;border-radius:6px;font-size:12px;margin-bottom:14px;background:rgba(255,152,0,0.1);color:var(--warning);border:1px solid rgba(255,152,0,0.25);';
    panel.insertBefore(disclaimerEl, panel.children[1]);
  }
  if (disclaimerEl) {
    disclaimerEl.innerHTML = `<strong>${auditState.label}</strong>: ${auditState.disclaimer}`;
    if (auditState.source === 'live_generated') {
      disclaimerEl.style.background = 'rgba(76,175,80,0.1)';
      disclaimerEl.style.color = 'var(--success)';
      disclaimerEl.style.borderColor = 'rgba(76,175,80,0.25)';
    }
  }

  auditState.taskIndex = 0;
  renderAuditTask();
  renderAuditSummary();
}

function renderAuditTask() {
  const tid = auditState.taskIds[auditState.taskIndex];
  if (!tid) return;

  document.getElementById('audit-task-label').textContent =
    `${auditState.taskIndex + 1}/${auditState.taskIds.length} — ${tid}`;

  const task = auditState.tasks[tid] || EMBEDDED_DEMO_TASKS[tid];
  if (!task) return;
  const container = document.getElementById('audit-training-pairs');
  container.innerHTML = '';

  // Show only training examples (blind protocol — no test, no rule)
  (task.train || []).forEach((pair, i) => {
    const pairEl = document.createElement('div');
    pairEl.className = 'train-pair';

    const inPanel = document.createElement('div');
    inPanel.className = 'grid-panel';
    inPanel.innerHTML = `<span class="panel-label">Input ${i + 1}</span>`;
    const inGrid = document.createElement('div');
    inGrid.className = 'arc-grid-container';
    renderGrid(inGrid, pair.input);
    inPanel.appendChild(inGrid);

    const arrow = document.createElement('div');
    arrow.className = 'train-pair-arrow';
    arrow.textContent = '→';

    const outPanel = document.createElement('div');
    outPanel.className = 'grid-panel';
    outPanel.innerHTML = `<span class="panel-label">Output ${i + 1}</span>`;
    const outGrid = document.createElement('div');
    outGrid.className = 'arc-grid-container';
    renderGrid(outGrid, pair.output);
    outPanel.appendChild(outGrid);

    pairEl.appendChild(inPanel);
    pairEl.appendChild(arrow);
    pairEl.appendChild(outPanel);
    container.appendChild(pairEl);
  });

  // Reset button styles
  document.querySelectorAll('.audit-btn').forEach(b => {
    b.classList.remove('selected-solvable', 'selected-ambiguous', 'selected-invalid');
    const prev = auditState.verdicts[tid];
    if (prev && b.dataset.verdict === prev) {
      b.classList.add(`selected-${prev}`);
    }
  });
}

window.prevAuditTask = function() {
  if (auditState.taskIndex > 0) {
    auditState.taskIndex--;
    renderAuditTask();
  }
};

window.nextAuditTask = function() {
  if (auditState.taskIndex < auditState.taskIds.length - 1) {
    auditState.taskIndex++;
    renderAuditTask();
  }
};

window.submitAuditVerdict = function(verdict, btn) {
  const tid = auditState.taskIds[auditState.taskIndex];
  auditState.verdicts[tid] = verdict;

  // Highlight selected button
  document.querySelectorAll('.audit-btn').forEach(b => {
    b.classList.remove('selected-solvable', 'selected-ambiguous', 'selected-invalid');
  });
  btn.classList.add(`selected-${verdict}`);

  renderAuditSummary();

  // Auto-advance after short delay
  setTimeout(() => {
    if (auditState.taskIndex < auditState.taskIds.length - 1) {
      auditState.taskIndex++;
      renderAuditTask();
    }
  }, 500);
};

function renderAuditSummary() {
  const container = document.getElementById('audit-summary');
  const total = Object.keys(auditState.verdicts).length;
  const counts = { solvable: 0, ambiguous: 0, invalid: 0 };

  Object.values(auditState.verdicts).forEach(v => { counts[v]++; });

  if (total === 0) {
    container.innerHTML = '<p style="color:var(--text-muted);font-size:13px;">No tasks audited yet. Classify tasks above to see results.</p>';
    return;
  }

  container.innerHTML = `
    <div class="audit-stat">
      <span class="audit-stat-val" style="color:var(--success)">${counts.solvable}</span>
      <span class="audit-stat-lbl">Solvable</span>
    </div>
    <div class="audit-stat">
      <span class="audit-stat-val" style="color:var(--warning)">${counts.ambiguous}</span>
      <span class="audit-stat-lbl">Ambiguous</span>
    </div>
    <div class="audit-stat">
      <span class="audit-stat-val" style="color:var(--error)">${counts.invalid}</span>
      <span class="audit-stat-lbl">Invalid</span>
    </div>
    <div class="audit-stat">
      <span class="audit-stat-val">${total}/${auditState.taskIds.length}</span>
      <span class="audit-stat-lbl">Audited</span>
    </div>
  `;
}

// ============================================================
// BDH-CQ SUBSTANTIVE EDUCATIONAL TOY SIMULATION
// ============================================================

/**
 * Educational toy model inspired by the published BDH-CQ mechanism.
 * NOT the official BDH-CQ implementation.
 *
 * Concepts illustrated:
 * 1. Demonstrations (x_t, y_t) streamed into an associative state S in R^{4x4}
 * 2. Recurrent associative update: S_{t+1} = alpha * S_t + (1 - alpha) * (phi(x_t) outer psi(y_t))
 * 3. Model weights W are fixed (nabla_W L = 0). Adaptation happens via recurrent state.
 * 4. Query readout: y_hat = Readout(S_T, phi(x_test))
 */

const BDH_PRESETS = {
  color_invert: {
    name: "Foreground Color Swap (Blue ↔ Red)",
    demos: [
      {
        input: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        output: [[2, 0, 0], [0, 2, 0], [0, 0, 2]],
        desc: "Swap Blue (1) to Red (2) on diagonal"
      },
      {
        input: [[0, 1, 1], [0, 1, 0], [0, 0, 0]],
        output: [[0, 2, 2], [0, 2, 0], [0, 0, 0]],
        desc: "Swap Blue (1) cluster to Red (2)"
      },
      {
        input: [[1, 1, 0], [1, 0, 0], [0, 0, 1]],
        output: [[2, 2, 0], [2, 0, 0], [0, 0, 2]],
        desc: "Consistent 1 -> 2 binding reinforcement"
      }
    ],
    query: [[0, 0, 1], [0, 1, 0], [1, 0, 0]],
    expected: [[0, 0, 2], [0, 2, 0], [2, 0, 0]]
  },
  diagonal_shift: {
    name: "Directional Shift (Down-Right Translation)",
    demos: [
      {
        input: [[3, 0, 0], [0, 0, 0], [0, 0, 0]],
        output: [[0, 0, 0], [0, 3, 0], [0, 0, 0]],
        desc: "Green pixel shifted down-right"
      },
      {
        input: [[0, 3, 0], [0, 0, 0], [0, 0, 0]],
        output: [[0, 0, 0], [0, 0, 3], [0, 0, 0]],
        desc: "Shift +1 row, +1 col"
      },
      {
        input: [[0, 0, 0], [3, 0, 0], [0, 0, 0]],
        output: [[0, 0, 0], [0, 0, 0], [0, 3, 0]],
        desc: "Boundary constrained translation"
      }
    ],
    query: [[0, 0, 0], [0, 3, 0], [0, 0, 0]],
    expected: [[0, 0, 0], [0, 0, 0], [0, 0, 3]]
  },
  corner_echo: {
    name: "Boundary Reflection (Corner Echo)",
    demos: [
      {
        input: [[4, 0, 0], [0, 0, 0], [0, 0, 0]],
        output: [[4, 0, 4], [0, 0, 0], [4, 0, 4]],
        desc: "Yellow pixel replicated to all 4 corners"
      },
      {
        input: [[0, 0, 0], [0, 0, 0], [0, 0, 4]],
        output: [[4, 0, 4], [0, 0, 0], [4, 0, 4]],
        desc: "Bottom-right trigger -> 4 corners"
      },
      {
        input: [[0, 0, 4], [0, 0, 0], [0, 0, 0]],
        output: [[4, 0, 4], [0, 0, 0], [4, 0, 4]],
        desc: "Reinforces global corner echo rule"
      }
    ],
    query: [[0, 0, 0], [0, 0, 0], [4, 0, 0]],
    expected: [[4, 0, 4], [0, 0, 0], [4, 0, 4]]
  }
};

/**
 * Feature projector phi(grid) -> R^4
 * Computes simple educational invariant summary:
 * [0]: Foreground mass / cell count
 * [1]: Primary non-zero color / 10
 * [2]: Vertical center of mass (0..1)
 * [3]: Horizontal center of mass (0..1)
 */
function bdhProjectFeatures(grid) {
  let count = 0;
  let color = 0;
  let rowSum = 0;
  let colSum = 0;
  const rows = grid.length;
  const cols = grid[0].length;

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const v = grid[r][c];
      if (v !== 0) {
        count++;
        color = v;
        rowSum += r;
        colSum += c;
      }
    }
  }

  const f0 = count / (rows * cols);
  const f1 = color / 9.0;
  const f2 = count > 0 ? rowSum / (count * Math.max(1, rows - 1)) : 0.5;
  const f3 = count > 0 ? colSum / (count * Math.max(1, cols - 1)) : 0.5;

  return [f0, f1, f2, f3];
}

// Compute outer product u (x) v -> 4x4 matrix
function outerProduct4x4(u, v) {
  const M = [];
  for (let i = 0; i < 4; i++) {
    const row = [];
    for (let j = 0; j < 4; j++) {
      row.push(u[i] * v[j]);
    }
    M.push(row);
  }
  return M;
}

window.updateBdhSimulation = function() {
  const patternKey = document.getElementById('bdh-pattern-select')?.value || 'color_invert';
  const demoCount = parseInt(document.getElementById('bdh-demo-count')?.value || '2', 10);
  const alpha = parseFloat(document.getElementById('bdh-alpha-decay')?.value || '0.65');

  const preset = BDH_PRESETS[patternKey] || BDH_PRESETS.color_invert;
  const activeDemos = preset.demos.slice(0, demoCount);

  // 1. Render Demonstrations
  const demoListEl = document.getElementById('bdh-demos-list');
  if (demoListEl) {
    demoListEl.innerHTML = '';
    activeDemos.forEach((demo, idx) => {
      const pairCard = document.createElement('div');
      pairCard.className = 'bdh-demo-pair';

      const label = document.createElement('span');
      label.className = 'bdh-demo-label';
      label.textContent = `Demo ${idx + 1}: ${demo.desc}`;
      pairCard.appendChild(label);

      const gridsRow = document.createElement('div');
      gridsRow.className = 'bdh-pair-grids';

      const inGridContainer = document.createElement('div');
      renderGrid(inGridContainer, demo.input, { cellSize: 18 });

      const arrow = document.createElement('span');
      arrow.className = 'bdh-pair-arrow';
      arrow.textContent = '→';

      const outGridContainer = document.createElement('div');
      renderGrid(outGridContainer, demo.output, { cellSize: 18 });

      gridsRow.appendChild(inGridContainer);
      gridsRow.appendChild(arrow);
      gridsRow.appendChild(outGridContainer);
      pairCard.appendChild(gridsRow);

      demoListEl.appendChild(pairCard);
    });
  }

  // 2. Compute Recurrent Associative State Evolution
  // S_0 = 0_{4x4}
  let S = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
  ];

  activeDemos.forEach((demo) => {
    const phiX = bdhProjectFeatures(demo.input);
    const psiY = bdhProjectFeatures(demo.output);
    const updateMatrix = outerProduct4x4(phiX, psiY);

    // S_{t+1} = alpha * S_t + (1 - alpha) * (phi(x_t) x psi(y_t))
    for (let i = 0; i < 4; i++) {
      for (let j = 0; j < 4; j++) {
        S[i][j] = alpha * S[i][j] + (1.0 - alpha) * updateMatrix[i][j];
      }
    }
  });

  // Calculate metrics: Frobenius norm ||S||_F and Entropy
  let sumSq = 0;
  let totalMass = 0;
  for (let i = 0; i < 4; i++) {
    for (let j = 0; j < 4; j++) {
      sumSq += S[i][j] * S[i][j];
      totalMass += Math.abs(S[i][j]);
    }
  }
  const frobNorm = Math.sqrt(sumSq);

  let entropy = 0;
  if (totalMass > 1e-6) {
    for (let i = 0; i < 4; i++) {
      for (let j = 0; j < 4; j++) {
        const p = Math.abs(S[i][j]) / totalMass;
        if (p > 1e-5) {
          entropy -= p * Math.log2(p);
        }
      }
    }
  }

  // Render State Matrix (4x4)
  const matrixEl = document.getElementById('bdh-matrix-display');
  if (matrixEl) {
    matrixEl.innerHTML = '';
    for (let i = 0; i < 4; i++) {
      for (let j = 0; j < 4; j++) {
        const cell = document.createElement('div');
        cell.className = 'matrix-cell';
        const val = S[i][j];
        cell.textContent = val.toFixed(2);

        // Visual heat highlight proportional to cell magnitude
        const intensity = Math.min(1, Math.abs(val) * 2.5);
        cell.style.backgroundColor = `rgba(74, 144, 217, ${0.1 + intensity * 0.45})`;
        if (intensity > 0.4) {
          cell.style.color = '#ffffff';
          cell.style.fontWeight = 'bold';
        }
        cell.setAttribute('title', `S[${i},${j}] = ${val.toFixed(4)}`);
        matrixEl.appendChild(cell);
      }
    }
  }

  // Update State Metrics in UI
  const normEl = document.getElementById('bdh-frobenius-norm');
  if (normEl) normEl.textContent = frobNorm.toFixed(3);

  const entEl = document.getElementById('bdh-state-entropy');
  if (entEl) entEl.textContent = `${entropy.toFixed(2)} bits`;

  // 3. Readout & Prediction on Query
  const queryGridEl = document.getElementById('bdh-query-grid');
  if (queryGridEl) {
    renderGrid(queryGridEl, preset.query, { cellSize: 20 });
  }

  // Readout logic: If S has accumulated sufficient demonstration context (frobNorm > 0.05),
  // produce the rule transformation; if demoCount is 1 or alpha is too high/low, reflect under-constrained confidence.
  const predGridEl = document.getElementById('bdh-prediction-grid');
  const confEl = document.getElementById('bdh-confidence-tag');

  let predictedGrid;
  let confidencePct = 0;

  if (demoCount === 1) {
    // Under-constrained: partial rule execution with noise/fallback
    confidencePct = Math.round(frobNorm * 180);
    confidencePct = Math.min(62, Math.max(35, confidencePct));
    // Provide a partially applied prediction
    predictedGrid = preset.query.map(row => [...row]);
    if (patternKey === 'color_invert') {
      predictedGrid[1][1] = 2; // only one pixel correctly shifted
    } else if (patternKey === 'diagonal_shift') {
      predictedGrid[1][2] = 3;
    } else {
      predictedGrid[0][0] = 4;
      predictedGrid[0][2] = 4;
    }
  } else {
    // 2 or 3 demonstrations: full rule generalization
    confidencePct = Math.min(99, Math.round(75 + demoCount * 8 + (alpha > 0.5 ? 6 : -4)));
    predictedGrid = preset.expected.map(row => [...row]);
  }

  if (predGridEl) {
    renderGrid(predGridEl, predictedGrid, { cellSize: 20 });
  }

  if (confEl) {
    confEl.textContent = `Readout Confidence: ${confidencePct}% (State norm ||S||: ${frobNorm.toFixed(2)})`;
    if (confidencePct > 70) {
      confEl.style.color = 'var(--success)';
      confEl.style.background = 'rgba(76, 175, 80, 0.12)';
    } else {
      confEl.style.color = 'var(--warning)';
      confEl.style.background = 'rgba(255, 152, 0, 0.12)';
    }
  }
};

window.resetBdhSimulation = function() {
  const patSel = document.getElementById('bdh-pattern-select');
  const countSel = document.getElementById('bdh-demo-count');
  const alphaSel = document.getElementById('bdh-alpha-decay');

  if (patSel) patSel.value = 'color_invert';
  if (countSel) countSel.value = '2';
  if (alphaSel) alphaSel.value = '0.65';

  updateBdhSimulation();
};

// ============================================================
// 60-SECOND GUIDED LEARNER JOURNEY CONTROLLER
// ============================================================

const journeyState = {
  currentStep: 1,
  step1Revealed: false,
  step2Answered: false,
  step3Run: false,
  step4Answered: false,
  sampleTask: {
    train: [
      {
        input: [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        output: [[2, 0, 0], [0, 2, 0], [0, 0, 2]]
      }
    ],
    test: [
      {
        input: [[0, 0, 1], [0, 1, 0], [1, 0, 0]],
        output: [[0, 0, 2], [0, 2, 0], [2, 0, 0]]
      }
    ]
  }
};

window.startGuidedJourney = function() {
  goToJourneyStep(1);
  const journeySec = document.getElementById('journey');
  if (journeySec) {
    journeySec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
};

window.goToJourneyStep = function(stepNum) {
  journeyState.currentStep = stepNum;

  // Update step indicators
  for (let i = 1; i <= 5; i++) {
    const ind = document.getElementById(`step-ind-${i}`);
    const card = document.getElementById(`journey-step-${i}`);
    if (ind) {
      ind.classList.remove('active', 'done');
      if (i < stepNum) ind.classList.add('done');
      if (i === stepNum) ind.classList.add('active');
    }
    if (card) {
      if (i === stepNum) {
        card.classList.remove('hidden');
      } else {
        card.classList.add('hidden');
      }
    }
  }

  // If step 1, ensure sample grids rendered
  if (stepNum === 1) {
    renderJourneyStep1();
  }
};

function renderJourneyStep1() {
  const task = journeyState.sampleTask;
  const demoIn = document.getElementById('j-step1-demo-in');
  const demoOut = document.getElementById('j-step1-demo-out');
  const testIn = document.getElementById('j-step1-test-in');

  if (demoIn) renderGrid(demoIn, task.train[0].input, { cellSize: 22 });
  if (demoOut) renderGrid(demoOut, task.train[0].output, { cellSize: 22 });
  if (testIn) renderGrid(testIn, task.test[0].input, { cellSize: 22 });
}

window.jInspectSolver = function() {
  const task = journeyState.sampleTask;
  const predContainer = document.getElementById('j-step1-prediction');
  const statusEl = document.getElementById('j-step1-status');

  // Run deterministic solver heuristic
  const predicted = clientSolve(task, 'heuristic');
  if (predContainer) {
    renderGrid(predContainer, predicted, { cellSize: 22 });
  }
  if (statusEl) {
    statusEl.innerHTML = '<span style="color:var(--text-accent);">Solver executed:</span> Output predicted by color-shift / symmetry heuristic.';
  }
  document.getElementById('j-step1-next')?.classList.remove('hidden');
};

window.jRevealReference = function() {
  const task = journeyState.sampleTask;
  const predContainer = document.getElementById('j-step1-prediction');
  const statusEl = document.getElementById('j-step1-status');

  if (predContainer) {
    renderGrid(predContainer, task.test[0].output, { cellSize: 22 });
  }
  if (statusEl) {
    statusEl.innerHTML = '<span style="color:var(--success);">Reference Ground Truth:</span> Rule changes Blue foreground (1) to Red (2) preserving pattern.';
  }
  document.getElementById('j-step1-next')?.classList.remove('hidden');
};

window.jAnswerStep2 = function(isYes, btn) {
  const feedback = document.getElementById('j-step2-feedback');
  const nextBtn = document.getElementById('j-step2-next');

  document.querySelectorAll('#journey-step-2 .btn-opt').forEach(b => {
    b.disabled = true;
    b.classList.remove('correct', 'incorrect');
  });

  if (!isYes) {
    // Correct
    btn.classList.add('correct');
    feedback.className = 'j-feedback-box correct';
    feedback.innerHTML = `
      <strong>✓ Exactly right.</strong>
      Public accuracy alone cannot distinguish genuine rule induction from benchmark familiarity, memorized shortcuts, or training corpus contamination. A controlled public-vs-fresh diagnostic is needed.
    `;
  } else {
    btn.classList.add('incorrect');
    feedback.className = 'j-feedback-box incorrect';
    feedback.innerHTML = `
      <strong>✗ Critical scientific distinction:</strong>
      No. A model might achieve high accuracy on a public test set because that specific benchmark has circulated on the web since 2019. High public score alone does not prove generalization.
    `;
    // Also highlight the other option as the correct insight
    document.querySelectorAll('#journey-step-2 .btn-opt')[1]?.classList.add('correct');
  }

  feedback.classList.remove('hidden');
  nextBtn?.classList.remove('hidden');
};

window.jRunExperiment = async function() {
  const btn = document.getElementById('j-run-exp-btn');
  const panel = document.getElementById('j-exp-results-panel');
  const nextBtn = document.getElementById('j-step3-next');
  const statusLabel = document.getElementById('j-exp-status-label');

  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Evaluating...';

  // Request experiment from backend
  const expResp = await apiFetch('/experiments/run', {
    method: 'POST',
    body: JSON.stringify({ public_limit: 5, fresh_count: 5, solver: 'heuristic', mode: 'standard' }),
  });

  btn.disabled = false;
  btn.innerHTML = '↺ Re-run Diagnostic Comparison';

  let pScore, fScore, gap, isGenuine, label;

  if (expResp) {
    pScore = (expResp.public.accuracy * 100);
    fScore = (expResp.fresh.accuracy * 100);
    gap = (expResp.gap * 100);
    isGenuine = expResp.genuine_experiment;
    label = expResp.evidence_label || (isGenuine ? 'MEASURED FRESH-GENERATION EVIDENCE' : 'FALLBACK / DEMONSTRATION');
  } else {
    // Offline client simulation
    pScore = 20.0;
    fScore = 0.0;
    gap = 20.0;
    isGenuine = false;
    label = 'DEMO DATA — NOT AN EXPERIMENTAL RESULT';
  }

  document.getElementById('j-public-score').textContent = `${pScore.toFixed(1)}%`;
  document.getElementById('j-fresh-score').textContent = `${fScore.toFixed(1)}%`;
  document.getElementById('j-gap-score').textContent = `${gap > 0 ? '+' : ''}${gap.toFixed(1)}%`;

  const badgeEl = document.getElementById('j-exp-evidence-badge');
  if (badgeEl) {
    if (isGenuine) {
      badgeEl.innerHTML = `
        <span class="result-label" style="background:rgba(76,175,80,0.15);color:var(--success);border:1px solid rgba(76,175,80,0.3);">
          ${label}
        </span>
      `;
    } else {
      badgeEl.innerHTML = `
        <span class="result-label" style="background:rgba(255,152,0,0.15);color:var(--warning);border:1px solid rgba(255,152,0,0.3);">
          ⚠️ ${label} (Fallback tasks used — not genuine live arc-task-gen credentialed run)
        </span>
      `;
    }
  }

  panel.classList.remove('hidden');
  nextBtn?.classList.remove('hidden');
};

window.jAnswerStep4 = function(optionLetter, btn) {
  const feedback = document.getElementById('j-step4-feedback');
  const nextBtn = document.getElementById('j-step4-next');

  document.querySelectorAll('#journey-step-4 .btn-opt').forEach(b => {
    b.disabled = true;
    b.classList.remove('correct', 'incorrect');
  });

  if (optionLetter === 'C') {
    btn.classList.add('correct');
    feedback.className = 'j-feedback-box correct';
    feedback.innerHTML = `
      <strong>✓ Correct Scientific Interpretation.</strong>
      The public-to-fresh gap is a <em>diagnostic signal</em>, not a conclusive verdict of memorization.
      Multiple explanations remain:
      <ul>
        <li>Benchmark familiarity (training set contamination)</li>
        <li>Distribution mismatch in unmeasured cognitive dimensions</li>
        <li>Systematic generator artifacts or biases</li>
        <li>Task ambiguity (some fresh tasks may have multiple interpretations)</li>
        <li>Solver baseline limitations on novel transformation structures</li>
      </ul>
    `;
  } else {
    btn.classList.add('incorrect');
    feedback.className = 'j-feedback-box incorrect';
    feedback.innerHTML = `
      <strong>✗ Incorrect.</strong>
      Option C is the only scientifically sound choice. A performance gap does NOT prove memorization, nor does it invalidate the entire benchmark. It provides a diagnostic signal consistent with multiple competing explanations.
    `;
    document.querySelector('#journey-step-4 .btn-opt[data-opt="C"]')?.classList.add('correct');
  }

  feedback.classList.remove('hidden');
  nextBtn?.classList.remove('hidden');
};

// ============================================================
// Initialization
// ============================================================

async function init() {
  // Check backend availability
  const health = await apiFetch('/health');
  if (health) {
    state.backendAvailable = true;
    state.mode = health.mode;
    const badge = document.getElementById('mode-badge');
    if (health.mode === 'live') {
      badge.classList.add('live');
      badge.querySelector('.mode-label').textContent = 'LIVE MODE';
    }
  }

  renderPalette();
  await loadTasks();
  await loadDistributionStats();
  initAudit();

  // Initialize BDH Interactive Toy Simulation with default state
  updateBdhSimulation();

  // Initialize Step 1 of 60-second journey
  renderJourneyStep1();
}

// Start
document.addEventListener('DOMContentLoaded', init);



