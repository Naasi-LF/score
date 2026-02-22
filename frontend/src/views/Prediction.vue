<template>
  <div>
    <h2 class="page-title">成绩预测</h2>

    <!-- Config bar -->
    <div class="config-bar">
      <div class="config-item">
        <label class="config-label">任务类型</label>
        <div class="seg-control">
          <button :class="['seg-btn', task === 'grade' ? 'active' : '']" @click="task = 'grade'; modelName = 'random_forest'">成绩预测 (G3)</button>
          <button :class="['seg-btn', task === 'risk' ? 'active' : '']" @click="task = 'risk'; modelName = 'random_forest'">风险预警</button>
        </div>
      </div>
      <div class="config-item">
        <label class="config-label">模型</label>
        <select class="config-select" v-model="modelName">
          <option value="random_forest">随机森林</option>
          <option value="svm">SVM</option>
          <option value="decision_tree">决策树</option>
          <option v-if="task === 'grade'" value="linear">线性回归</option>
          <option v-else value="logistic">逻辑回归</option>
        </select>
      </div>
      <button class="btn-predict" :disabled="!selected.length || loading" @click="handlePredict">
        {{ loading ? '预测中...' : `预测已选 ${selected.length} 名学生` }}
      </button>
    </div>

    <!-- Student table -->
    <div class="card">
      <div class="card-header">
        <span>选择学生（可多选）</span>
        <span class="hint">已选 {{ selected.length }} 人</span>
      </div>
      <div class="table-wrap" v-loading="loadingStudents">
        <table class="data-table">
          <thead>
            <tr>
              <th style="width:40px">
                <input type="checkbox" :checked="allChecked" @change="toggleAll" />
              </th>
              <th>ID</th><th>姓名</th><th>年龄</th><th>性别</th>
              <th>G1</th><th>G2</th><th>学习时长</th><th>不及格</th><th>缺勤</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in students" :key="s.id" :class="{ selected: selected.includes(s.id) }" @click="toggleSelect(s.id)" style="cursor:pointer">
              <td @click.stop><input type="checkbox" :checked="selected.includes(s.id)" @change="toggleSelect(s.id)" /></td>
              <td class="mono">{{ s.id }}</td>
              <td>{{ s.name }}</td>
              <td class="mono">{{ s.age }}</td>
              <td><span class="badge" :class="s.sex === 'M' ? 'badge-blue' : 'badge-pink'">{{ s.sex === 'M' ? '男' : '女' }}</span></td>
              <td class="mono">{{ s.g1 }}</td>
              <td class="mono">{{ s.g2 }}</td>
              <td class="mono">{{ s.studytime }}</td>
              <td class="mono" :class="s.failures > 0 ? 'text-warn' : ''">{{ s.failures }}</td>
              <td class="mono" :class="s.absences > 10 ? 'text-warn' : ''">{{ s.absences }}</td>
            </tr>
            <tr v-if="!students.length && !loadingStudents">
              <td colspan="10" class="empty">暂无学生数据，请先在「学生管理」中导入</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="pagination">
        <button class="page-btn" :disabled="page === 1" @click="loadStudents(page - 1)">‹ 上一页</button>
        <span class="page-info">第 {{ page }} 页 / 共 {{ Math.max(1, Math.ceil(total / pageSize)) }} 页</span>
        <button class="page-btn" :disabled="page >= Math.ceil(total / pageSize)" @click="loadStudents(page + 1)">下一页 ›</button>
      </div>
    </div>

    <!-- Results -->
    <div class="card" v-if="results.length">
      <div class="card-header">预测结果</div>
      <table class="data-table">
        <thead>
          <tr>
            <th>学生ID</th><th>姓名</th><th>G1</th><th>G2</th>
            <th v-if="task === 'grade'">预测 G3</th>
            <th v-else>风险等级</th>
            <th v-if="task === 'risk'">风险概率</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="r in results" :key="r.student_id">
            <td class="mono">{{ r.student_id }}</td>
            <td>{{ r.name }}</td>
            <td class="mono">{{ r.g1 }}</td>
            <td class="mono">{{ r.g2 }}</td>
            <td v-if="task === 'grade'" class="mono score">{{ r.result.toFixed(1) }} <span class="unit">/ 20</span></td>
            <td v-else>
              <span class="badge" :class="r.result >= 0.5 ? 'badge-danger' : 'badge-success'">
                {{ r.result >= 0.5 ? '高风险' : '低风险' }}
              </span>
            </td>
            <td v-if="task === 'risk'" class="mono">{{ r.probability != null ? (r.probability * 100).toFixed(1) + '%' : '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '../api/index.js'

const task = ref('grade')
const modelName = ref('random_forest')
const loading = ref(false)
const loadingStudents = ref(false)
const students = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const selected = ref([])
const results = ref([])

const allChecked = computed(() =>
  students.value.length > 0 && students.value.every(s => selected.value.includes(s.id))
)

function toggleAll() {
  if (allChecked.value) {
    selected.value = selected.value.filter(id => !students.value.find(s => s.id === id))
  } else {
    const ids = students.value.map(s => s.id)
    selected.value = [...new Set([...selected.value, ...ids])]
  }
}

function toggleSelect(id) {
  const idx = selected.value.indexOf(id)
  if (idx === -1) selected.value.push(id)
  else selected.value.splice(idx, 1)
}

async function loadStudents(p = 1) {
  loadingStudents.value = true
  page.value = p
  try {
    const res = await api.get('/students', { params: { skip: (p - 1) * pageSize, limit: pageSize } })
    students.value = res.data.items
    total.value = res.data.total
  } finally {
    loadingStudents.value = false
  }
}

async function handlePredict() {
  loading.value = true
  results.value = []
  const toPredict = students.value.filter(s => selected.value.includes(s.id))
  const out = []
  for (const s of toPredict) {
    try {
      const res = await api.post('/predictions/single', {
        task: task.value,
        model_name: modelName.value,
        student_id: s.id,
        features: {
          g1: s.g1, g2: s.g2, studytime: s.studytime, failures: s.failures,
          absences: s.absences, age: s.age, medu: s.medu, fedu: s.fedu,
          sex: s.sex, address: s.address, famsize: s.famsize, activities: s.activities,
        }
      })
      out.push({ student_id: s.id, name: s.name, g1: s.g1, g2: s.g2, ...res.data })
    } catch (e) {
      ElMessage.error(`学生 ${s.name} 预测失败：${e.response?.data?.detail || '请先训练模型'}`)
    }
  }
  results.value = out
  loading.value = false
}

onMounted(() => loadStudents())
</script>

<style scoped>
.config-bar {
  display: flex;
  align-items: flex-end;
  gap: 24px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.config-item { display: flex; flex-direction: column; gap: 6px; }
.config-label { font-size: 12px; color: #909399; font-weight: 500; }

.seg-control { display: flex; border: 1px solid #dcdfe6; border-radius: 6px; overflow: hidden; }
.seg-btn {
  padding: 7px 16px;
  font-size: 13px;
  background: #fff;
  border: none;
  cursor: pointer;
  color: #606266;
  transition: background 0.15s, color 0.15s;
}
.seg-btn + .seg-btn { border-left: 1px solid #dcdfe6; }
.seg-btn.active { background: #409eff; color: #fff; }

.config-select {
  padding: 7px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 13px;
  color: #303133;
  background: #fff;
  outline: none;
  cursor: pointer;
}

.btn-predict {
  margin-left: auto;
  padding: 8px 24px;
  background: #409eff;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  align-self: flex-end;
}
.btn-predict:hover:not(:disabled) { background: #337ecc; }
.btn-predict:disabled { opacity: 0.5; cursor: not-allowed; }

.card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 16px;
  overflow: hidden;
}
.card-header {
  padding: 12px 20px;
  border-bottom: 1px solid #f0f0f0;
  font-weight: 600;
  font-size: 14px;
  color: #303133;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.hint { font-size: 12px; color: #409eff; font-weight: 400; }

.table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th {
  padding: 10px 14px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #909399;
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
  white-space: nowrap;
}
.data-table td {
  padding: 10px 14px;
  font-size: 13px;
  color: #303133;
  border-bottom: 1px solid #f5f5f5;
}
.data-table tr:last-child td { border-bottom: none; }
.data-table tr.selected td { background: #ecf5ff; }
.data-table tr:hover td { background: #f5f7fa; }
.data-table tr.selected:hover td { background: #d9ecff; }

.mono { font-family: 'JetBrains Mono', monospace; }
.score { color: #409eff; font-weight: 600; }
.unit { font-size: 11px; color: #909399; }
.text-warn { color: #e6a23c; }
.empty { text-align: center; color: #909399; padding: 32px !important; }

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}
.badge-blue { background: #ecf5ff; color: #409eff; }
.badge-pink { background: #fdf2f8; color: #e91e8c; }
.badge-success { background: #f0f9eb; color: #67c23a; }
.badge-danger { background: #fef0f0; color: #f56c6c; }

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 12px;
  border-top: 1px solid #f0f0f0;
}
.page-btn {
  padding: 5px 14px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
  color: #606266;
  font-size: 13px;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
}
.page-btn:hover:not(:disabled) { border-color: #409eff; color: #409eff; }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-info { font-size: 13px; color: #909399; }
</style>
