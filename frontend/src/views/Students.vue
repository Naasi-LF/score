<template>
  <div>
    <h2 class="page-title">学生管理</h2>
    <div class="toolbar">
      <button class="btn-primary" @click="showAdd = true">＋ 新增学生</button>
      <el-upload :before-upload="handleImport" accept=".csv,.xlsx" :show-file-list="false" style="display:inline-block">
        <button class="btn-ghost">↑ 批量导入 CSV</button>
      </el-upload>
      <span class="total-badge">共 {{ total }} 条记录</span>
    </div>

    <div class="table-wrap" v-loading="loading">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th><th>姓名</th><th>年龄</th><th>性别</th>
            <th>G1</th><th>G2</th><th>学习时长</th><th>不及格</th><th>缺勤</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in students" :key="s.id">
            <td class="mono">{{ s.id }}</td>
            <td>{{ s.name }}</td>
            <td class="mono">{{ s.age }}</td>
            <td><span class="badge" :class="s.sex === 'M' ? 'badge-blue' : 'badge-pink'">{{ s.sex === 'M' ? '男' : '女' }}</span></td>
            <td class="mono score">{{ s.g1 }}</td>
            <td class="mono score">{{ s.g2 }}</td>
            <td class="mono">{{ s.studytime }}</td>
            <td class="mono" :class="s.failures > 0 ? 'warn' : ''">{{ s.failures }}</td>
            <td class="mono" :class="s.absences > 10 ? 'warn' : ''">{{ s.absences }}</td>
            <td><button class="btn-danger-sm" @click="handleDelete(s.id)">删除</button></td>
          </tr>
          <tr v-if="!students.length && !loading">
            <td colspan="10" class="empty">暂无数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button class="page-btn" :disabled="page === 1" @click="onPageChange(page - 1)">‹</button>
      <span class="page-info">{{ page }} / {{ Math.max(1, Math.ceil(total / pageSize)) }}</span>
      <button class="page-btn" :disabled="page >= Math.ceil(total / pageSize)" @click="onPageChange(page + 1)">›</button>
    </div>

    <!-- Add dialog -->
    <div v-if="showAdd" class="modal-overlay" @click.self="showAdd = false">
      <div class="modal">
        <div class="modal-header">
          <span>新增学生</span>
          <button class="modal-close" @click="showAdd = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="field"><label>姓名</label><input v-model="form.name" class="finput" /></div>
            <div class="field"><label>年龄</label><input v-model.number="form.age" type="number" min="10" max="25" class="finput" /></div>
            <div class="field">
              <label>性别</label>
              <select v-model="form.sex" class="fselect">
                <option value="M">男 (M)</option><option value="F">女 (F)</option>
              </select>
            </div>
            <div class="field">
              <label>住址</label>
              <select v-model="form.address" class="fselect">
                <option value="U">城市 (U)</option><option value="R">农村 (R)</option>
              </select>
            </div>
            <div class="field">
              <label>家庭规模</label>
              <select v-model="form.famsize" class="fselect">
                <option value="GT3">&gt;3人 (GT3)</option><option value="LE3">≤3人 (LE3)</option>
              </select>
            </div>
            <div class="field">
              <label>课外活动</label>
              <select v-model="form.activities" class="fselect">
                <option value="yes">有</option><option value="no">无</option>
              </select>
            </div>
            <div class="field"><label>母亲学历 (0-4)</label><input v-model.number="form.medu" type="number" min="0" max="4" class="finput" /></div>
            <div class="field"><label>父亲学历 (0-4)</label><input v-model.number="form.fedu" type="number" min="0" max="4" class="finput" /></div>
            <div class="field"><label>学习时长 (1-4)</label><input v-model.number="form.studytime" type="number" min="1" max="4" class="finput" /></div>
            <div class="field"><label>不及格次数</label><input v-model.number="form.failures" type="number" min="0" max="4" class="finput" /></div>
            <div class="field"><label>缺勤次数</label><input v-model.number="form.absences" type="number" min="0" class="finput" /></div>
            <div class="field"><label>G1 成绩 (0-20)</label><input v-model.number="form.g1" type="number" min="0" max="20" class="finput" /></div>
            <div class="field"><label>G2 成绩 (0-20)</label><input v-model.number="form.g2" type="number" min="0" max="20" class="finput" /></div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-ghost" @click="showAdd = false">取消</button>
          <button class="btn-primary" @click="submitAdd">确认添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api/index.js'

const students = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)
const showAdd = ref(false)

const defaultForm = () => ({
  name: '', age: 17, sex: 'M', address: 'U', famsize: 'GT3',
  medu: 2, fedu: 2, studytime: 2, failures: 0, absences: 0,
  activities: 'no', g1: 10, g2: 10,
})
const form = ref(defaultForm())

async function fetchStudents() {
  loading.value = true
  try {
    const res = await api.get('/students', { params: { skip: (page.value - 1) * pageSize, limit: pageSize } })
    students.value = res.data.items
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

async function submitAdd() {
  await api.post('/students', form.value)
  ElMessage.success('添加成功')
  showAdd.value = false
  form.value = defaultForm()
  fetchStudents()
}

async function handleDelete(id) {
  await ElMessageBox.confirm('确认删除该学生？', '提示', { type: 'warning' })
  await api.delete(`/students/${id}`)
  ElMessage.success('已删除')
  fetchStudents()
}

async function handleImport(file) {
  const fd = new FormData()
  fd.append('file', file)
  const res = await api.post('/students/import', fd)
  ElMessage.success(`成功导入 ${res.data.imported} 条记录`)
  fetchStudents()
  return false
}

function onPageChange(p) {
  page.value = p
  fetchStudents()
}

onMounted(fetchStudents)
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.total-badge {
  margin-left: auto;
  font-size: 12px;
  color: #909399;
}

.btn-primary {
  background: #409eff;
  color: #fff;
  border: none;
  padding: 8px 18px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}
.btn-primary:hover { background: #337ecc; }

.btn-ghost {
  background: transparent;
  color: #606266;
  border: 1px solid #dcdfe6;
  padding: 8px 18px;
  font-size: 13px;
  cursor: pointer;
  border-radius: 4px;
  transition: border-color 0.2s, color 0.2s;
}
.btn-ghost:hover { border-color: #409eff; color: #409eff; }

.table-wrap {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #fafafa;
  padding: 10px 14px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  border-bottom: 1px solid #e4e7ed;
}

.data-table td {
  padding: 10px 14px;
  border-bottom: 1px solid #f0f0f0;
  color: #303133;
  font-size: 13px;
}

.data-table tr:last-child td { border-bottom: none; }
.data-table tbody tr:hover { background: #f5f7fa; }

.mono { font-family: monospace; font-size: 13px; }
.score { color: #409eff; font-weight: 600; }
.warn { color: #e6a23c; }

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 12px;
  font-weight: 600;
}
.badge-blue { background: #ecf5ff; color: #409eff; }
.badge-pink { background: #fdf2f8; color: #c2185b; }

.btn-danger-sm {
  background: transparent;
  border: 1px solid #fbc4c4;
  color: #f56c6c;
  padding: 3px 10px;
  font-size: 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
}
.btn-danger-sm:hover { background: #fef0f0; }

.empty {
  text-align: center;
  color: #909399;
  font-size: 13px;
  padding: 40px !important;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
}

.page-btn {
  background: #fff;
  border: 1px solid #dcdfe6;
  color: #606266;
  width: 32px;
  height: 32px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: border-color 0.2s, color 0.2s;
}
.page-btn:hover:not(:disabled) { border-color: #409eff; color: #409eff; }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.page-info {
  font-size: 13px;
  color: #909399;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #fff;
  border-radius: 10px;
  width: 620px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 24px rgba(0,0,0,0.15);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  font-size: 15px;
  font-weight: 700;
  color: #303133;
}

.modal-close {
  background: none;
  border: none;
  color: #909399;
  cursor: pointer;
  font-size: 16px;
  padding: 2px 6px;
  border-radius: 3px;
  transition: color 0.2s;
}
.modal-close:hover { color: #f56c6c; }

.modal-body { padding: 20px; overflow-y: auto; }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.field { display: flex; flex-direction: column; gap: 5px; }
.field label {
  font-size: 12px;
  font-weight: 500;
  color: #606266;
}

.finput, .fselect {
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  color: #303133;
  padding: 8px 10px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.2s;
  width: 100%;
}
.finput:focus, .fselect:focus { border-color: #409eff; }

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  border-top: 1px solid #e4e7ed;
}
</style>
