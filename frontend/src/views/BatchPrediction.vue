<template>
  <div>
    <h2 class="page-title">批量预测</h2>

    <div class="config-card">
      <div class="config-row">
        <div class="config-field">
          <label class="field-label">任务类型</label>
          <div class="seg-control">
            <button :class="['seg-btn', task === 'grade' ? 'active' : '']" @click="task = 'grade'; modelName = 'random_forest'">成绩预测</button>
            <button :class="['seg-btn', task === 'risk' ? 'active' : '']" @click="task = 'risk'; modelName = 'random_forest'">风险预警</button>
          </div>
        </div>
        <div class="config-field">
          <label class="field-label">模型</label>
          <select class="field-select" v-model="modelName">
            <option value="random_forest">随机森林</option>
            <option value="svm">SVM</option>
            <option value="decision_tree">决策树</option>
            <option v-if="task === 'grade'" value="linear">线性回归</option>
            <option v-else value="logistic">逻辑回归</option>
          </select>
        </div>
        <div class="config-field upload-field">
          <label class="field-label">上传文件</label>
          <el-upload :before-upload="handleUpload" accept=".csv,.xlsx" :show-file-list="false">
            <button class="btn-upload" :class="{ loading }" :disabled="loading">
              <span v-if="!loading">↑ 选择文件并预测</span>
              <span v-else class="blink">PROCESSING...</span>
            </button>
          </el-upload>
        </div>
      </div>
      <div class="hint-bar">
        <span class="hint-icon">ℹ</span>
        CSV 需包含列: <span class="hint-cols">age, medu, fedu, studytime, failures, absences, g1, g2, sex, address, famsize, activities</span>
      </div>
    </div>

    <div class="results-card" v-if="results.length">
      <div class="results-header">
        <div class="results-title">
          <span class="tag-label">OUTPUT</span>
          预测结果
          <span class="count-badge">{{ results.length }} 条</span>
        </div>
        <button class="btn-download" @click="downloadCSV">↓ 下载 CSV</button>
      </div>
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th v-for="col in resultCols" :key="col">{{ col }}</th>
              <th>预测值</th>
              <th>概率</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in results" :key="i">
              <td v-for="col in resultCols" :key="col" class="mono">{{ row[col] }}</td>
              <td>
                <span v-if="task === 'grade'" class="mono score-val">{{ Number(row.prediction).toFixed(2) }}</span>
                <span v-else :class="['risk-tag', row.prediction >= 0.5 ? 'risk-high' : 'risk-low']">
                  {{ row.prediction >= 0.5 ? '高风险' : '低风险' }}
                </span>
              </td>
              <td class="mono prob-val">{{ row.probability != null ? (row.probability * 100).toFixed(1) + '%' : '—' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="empty-state" v-else>
      <div class="empty-icon">▦</div>
      <div class="empty-text">上传 CSV 文件开始批量预测</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api/index.js'

const task = ref('grade')
const modelName = ref('random_forest')
const loading = ref(false)
const results = ref([])

const resultCols = computed(() => {
  if (!results.value.length) return []
  return Object.keys(results.value[0]).filter(k => !['prediction', 'probability', 'error'].includes(k))
})

async function handleUpload(file) {
  loading.value = true
  const fd = new FormData()
  fd.append('file', file)
  try {
    const res = await api.post(`/predictions/batch?task=${task.value}&model_name=${modelName.value}`, fd)
    results.value = res.data.results
    ElMessage.success(`完成 ${res.data.count} 条预测`)
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '预测失败')
  } finally {
    loading.value = false
  }
  return false
}

function downloadCSV() {
  if (!results.value.length) return
  const keys = Object.keys(results.value[0])
  const rows = [keys.join(','), ...results.value.map(r => keys.map(k => r[k] ?? '').join(','))]
  const blob = new Blob([rows.join('\n')], { type: 'text/csv' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `batch_result_${task.value}.csv`
  a.click()
}
</script>

<style scoped>
.config-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.config-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  align-items: flex-end;
  margin-bottom: 16px;
}

.config-field { display: flex; flex-direction: column; gap: 6px; }
.upload-field { flex: 1; }

.field-label {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.seg-control { display: flex; border: 1px solid var(--border); border-radius: 4px; overflow: hidden; }
.seg-btn {
  padding: 7px 16px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}
.seg-btn.active { background: var(--accent-dim); color: var(--accent); }
.seg-btn:hover:not(.active) { background: rgba(255,255,255,0.04); }

.field-select {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 12px;
  padding: 7px 10px;
  outline: none;
  min-width: 140px;
}
.field-select:focus { border-color: var(--accent); }

.btn-upload {
  padding: 8px 20px;
  background: var(--accent-dim);
  border: 1px solid var(--accent);
  border-radius: 4px;
  color: var(--accent);
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.06em;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-upload:hover { background: rgba(0,212,255,0.25); box-shadow: var(--accent-glow); }
.btn-upload.loading { opacity: 0.6; cursor: not-allowed; }

.blink { animation: blink 1s step-end infinite; }
@keyframes blink { 50% { opacity: 0; } }

.hint-bar {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
  background: rgba(0,212,255,0.04);
  border: 1px solid rgba(0,212,255,0.1);
  border-radius: 4px;
  padding: 8px 12px;
}
.hint-icon { color: var(--accent); margin-right: 6px; }
.hint-cols { color: var(--text-secondary); }

.results-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
}

.results-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-primary);
}

.tag-label {
  font-family: var(--font-mono);
  font-size: 10px;
  background: var(--accent-dim);
  color: var(--accent);
  border: 1px solid rgba(0,212,255,0.3);
  border-radius: 3px;
  padding: 1px 6px;
  letter-spacing: 0.1em;
}

.count-badge {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
  font-weight: 400;
  text-transform: none;
  letter-spacing: 0;
}

.btn-download {
  padding: 6px 14px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 4px;
  color: var(--text-secondary);
  font-family: var(--font-mono);
  font-size: 11px;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-download:hover { border-color: var(--accent); color: var(--accent); }

.table-wrap { overflow-x: auto; max-height: 480px; overflow-y: auto; }

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.data-table th {
  background: var(--bg-surface);
  color: var(--text-muted);
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
}
.data-table td {
  padding: 8px 12px;
  border-bottom: 1px solid rgba(30,45,69,0.6);
  color: var(--text-primary);
}
.data-table tr:hover td { background: rgba(0,212,255,0.03); }

.mono { font-family: var(--font-mono); }
.score-val { color: var(--accent); font-weight: 600; }
.prob-val { color: var(--text-secondary); }

.risk-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 3px;
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.06em;
}
.risk-high { background: rgba(239,68,68,0.15); color: var(--danger); border: 1px solid rgba(239,68,68,0.3); }
.risk-low  { background: rgba(16,185,129,0.15); color: var(--success); border: 1px solid rgba(16,185,129,0.3); }

.empty-state {
  text-align: center;
  padding: 80px 0;
  color: var(--text-muted);
}
.empty-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.3; }
.empty-text { font-family: var(--font-mono); font-size: 13px; letter-spacing: 0.06em; }
</style>
