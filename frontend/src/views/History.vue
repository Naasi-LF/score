<template>
  <div>
    <h2 class="page-title">预测历史</h2>

    <div class="filter-bar">
      <div class="filter-field">
        <label class="field-label">任务类型</label>
        <div class="seg-control">
          <button :class="['seg-btn', taskFilter === '' ? 'active' : '']" @click="taskFilter = ''; fetchHistory()">全部</button>
          <button :class="['seg-btn', taskFilter === 'grade' ? 'active' : '']" @click="taskFilter = 'grade'; fetchHistory()">成绩预测</button>
          <button :class="['seg-btn', taskFilter === 'risk' ? 'active' : '']" @click="taskFilter = 'risk'; fetchHistory()">风险预警</button>
        </div>
      </div>
      <button class="btn-ghost" @click="fetchHistory()">↻ 刷新</button>
    </div>

    <div class="table-wrap" v-loading="loading">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>任务</th>
            <th>模型</th>
            <th>预测结果</th>
            <th>概率</th>
            <th>学号</th>
            <th>时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in records" :key="r.id">
            <td class="mono">{{ r.id }}</td>
            <td>
              <span class="badge" :class="r.task === 'grade' ? 'badge-blue' : 'badge-orange'">
                {{ r.task === 'grade' ? '成绩预测' : '风险预警' }}
              </span>
            </td>
            <td class="mono">{{ r.model_name }}</td>
            <td>
              <span v-if="r.task === 'grade'" class="mono score-val">{{ Number(r.result).toFixed(2) }}</span>
              <span v-else class="badge" :class="r.result >= 0.5 ? 'badge-danger' : 'badge-success'">
                {{ r.result >= 0.5 ? '高风险' : '低风险' }}
              </span>
            </td>
            <td class="mono">{{ r.probability != null ? (r.probability * 100).toFixed(1) + '%' : '—' }}</td>
            <td class="mono">{{ r.student_no ?? '—' }}</td>
            <td class="mono time-col">{{ new Date(r.created_at).toLocaleString('zh-CN') }}</td>
          </tr>
          <tr v-if="!records.length && !loading">
            <td colspan="7" class="empty">暂无预测记录</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button class="page-btn" :disabled="page === 1" @click="onPageChange(page - 1)">‹</button>
      <span class="page-info">{{ page }} / {{ Math.max(1, Math.ceil(total / pageSize)) }}</span>
      <button class="page-btn" :disabled="page >= Math.ceil(total / pageSize)" @click="onPageChange(page + 1)">›</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/index.js'

const records = ref([])
const loading = ref(false)
const taskFilter = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)

async function fetchHistory() {
  loading.value = true
  try {
    const params = { skip: (page.value - 1) * pageSize, limit: pageSize }
    if (taskFilter.value) params.task = taskFilter.value
    const res = await api.get('/predictions/history', { params })
    records.value = res.data
    total.value = res.data.length < pageSize
      ? (page.value - 1) * pageSize + res.data.length
      : page.value * pageSize + 1
  } finally {
    loading.value = false
  }
}

function onPageChange(p) {
  page.value = p
  fetchHistory()
}

onMounted(fetchHistory)
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: flex-end;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filter-field { display: flex; flex-direction: column; gap: 6px; }

.field-label {
  font-size: 12px;
  font-weight: 500;
  color: #606266;
}

.seg-control { display: flex; border: 1px solid #dcdfe6; border-radius: 4px; overflow: hidden; }
.seg-btn {
  padding: 6px 14px;
  background: transparent;
  border: none;
  color: #606266;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
  border-right: 1px solid #dcdfe6;
}
.seg-btn:last-child { border-right: none; }
.seg-btn:hover { background: #ecf5ff; color: #409eff; }
.seg-btn.active { background: #ecf5ff; color: #409eff; font-weight: 600; }

.btn-ghost {
  padding: 7px 16px;
  background: transparent;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  color: #606266;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-ghost:hover { border-color: #409eff; color: #409eff; }

.table-wrap {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.data-table { width: 100%; border-collapse: collapse; }
.data-table th {
  padding: 10px 14px;
  background: #fafafa;
  border-bottom: 1px solid #e4e7ed;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  text-align: left;
}
.data-table td {
  padding: 10px 14px;
  border-bottom: 1px solid #f0f0f0;
  color: #303133;
  font-size: 13px;
}
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #f5f7fa; }

.mono { font-family: monospace; font-size: 12px; }
.score-val { color: #409eff; font-weight: 600; }
.time-col { color: #909399; font-size: 12px; }

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 500;
}
.badge-blue    { background: #ecf5ff; color: #409eff; }
.badge-orange  { background: #fdf6ec; color: #e6a23c; }
.badge-success { background: #f0f9eb; color: #67c23a; }
.badge-danger  { background: #fef0f0; color: #f56c6c; }

.empty {
  text-align: center;
  padding: 40px;
  color: #909399;
  font-size: 13px;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
  padding: 8px 0;
}
.page-btn {
  width: 32px; height: 32px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  color: #606266;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.15s;
  display: flex; align-items: center; justify-content: center;
}
.page-btn:hover:not(:disabled) { border-color: #409eff; color: #409eff; }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-info {
  font-size: 13px;
  color: #909399;
}
</style>
