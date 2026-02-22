<template>
  <div>
    <h2 class="page-title">模型对比</h2>

    <div class="tab-bar">
      <button :class="['tab-btn', activeTab === 'grade' ? 'active' : '']" @click="switchTab('grade')">
        <span class="tab-icon">◈</span> 成绩预测 (回归)
      </button>
      <button :class="['tab-btn', activeTab === 'risk' ? 'active' : '']" @click="switchTab('risk')">
        <span class="tab-icon">⚠</span> 风险预警 (分类)
      </button>
    </div>

    <div class="chart-card" style="margin-bottom:20px">
      <div class="card-header">各模型指标对比</div>
      <v-chart :option="barOption" style="height:320px" autoresize />
    </div>

    <div class="bottom-grid">
      <div class="chart-card">
        <div class="card-header">特征重要性 · 随机森林</div>
        <v-chart :option="importanceOption" style="height:300px" autoresize />
      </div>
      <div class="chart-card">
        <div class="card-header">指标详情</div>
        <div class="metrics-table-wrap">
          <table class="metrics-table">
            <thead>
              <tr>
                <th>模型</th>
                <template v-if="activeTab === 'grade'">
                  <th>MAE</th><th>RMSE</th><th>R²</th>
                </template>
                <template v-else>
                  <th>Acc</th><th>Prec</th><th>Recall</th><th>F1</th><th>AUC</th>
                </template>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in tableData" :key="row.model_name">
                <td class="model-name">{{ row.model_name }}</td>
                <template v-if="activeTab === 'grade'">
                  <td class="mono">{{ row.mae?.toFixed(3) ?? '—' }}</td>
                  <td class="mono">{{ row.rmse?.toFixed(3) ?? '—' }}</td>
                  <td class="mono" :class="row.r2 > 0.8 ? 'good' : ''">{{ row.r2?.toFixed(3) ?? '—' }}</td>
                </template>
                <template v-else>
                  <td class="mono" :class="row.accuracy > 0.8 ? 'good' : ''">{{ row.accuracy?.toFixed(3) ?? '—' }}</td>
                  <td class="mono">{{ row.precision?.toFixed(3) ?? '—' }}</td>
                  <td class="mono">{{ row.recall?.toFixed(3) ?? '—' }}</td>
                  <td class="mono" :class="row.f1 > 0.8 ? 'good' : ''">{{ row.f1?.toFixed(3) ?? '—' }}</td>
                  <td class="mono">{{ row.roc_auc?.toFixed(3) ?? '—' }}</td>
                </template>
              </tr>
              <tr v-if="!tableData.length">
                <td colspan="6" class="empty">暂无数据，请先训练模型</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import api from '../api/index.js'

use([BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

const activeTab = ref('grade')
const metrics = ref([])
const importance = ref({})

onMounted(async () => {
  const [m, imp] = await Promise.all([
    api.get('/analytics/model-comparison'),
    api.get('/analytics/feature-importance', { params: { task: 'grade', model_name: 'random_forest' } }),
  ])
  metrics.value = m.data
  importance.value = imp.data
})

async function switchTab(tab) {
  activeTab.value = tab
  const res = await api.get('/analytics/feature-importance', {
    params: { task: tab, model_name: 'random_forest' }
  })
  importance.value = res.data
}

const tableData = computed(() => metrics.value.filter(m => m.task === activeTab.value))

const COLORS = ['#409eff', '#f97316', '#67c23a', '#e6a23c', '#a78bfa']

const barOption = computed(() => {
  const rows = tableData.value
  if (!rows.length) return {}
  const models = rows.map(r => r.model_name)
  const isGrade = activeTab.value === 'grade'
  const metricKeys = isGrade ? ['mae', 'rmse', 'r2'] : ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
  const metricLabels = isGrade ? ['MAE', 'RMSE', 'R²'] : ['Accuracy', 'Precision', 'Recall', 'F1', 'ROC-AUC']
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, backgroundColor: '#fff', borderColor: '#e4e7ed', textStyle: { color: '#303133' } },
    legend: { data: metricLabels, textStyle: { color: '#606266', fontSize: 11 } },
    grid: { left: 16, right: 16, bottom: 16, top: 48, containLabel: true },
    xAxis: { type: 'category', data: models, axisLine: { lineStyle: { color: '#e4e7ed' } }, axisLabel: { color: '#606266', fontSize: 11 } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f0f0f0' } }, axisLabel: { color: '#909399', fontSize: 11 } },
    series: metricKeys.map((key, i) => ({
      name: metricLabels[i],
      type: 'bar',
      data: rows.map(r => r[key] ?? 0),
      itemStyle: { color: COLORS[i % COLORS.length] },
      barMaxWidth: 32,
    }))
  }
})

const importanceOption = computed(() => {
  const entries = Object.entries(importance.value).sort((a, b) => b[1] - a[1]).slice(0, 10)
  if (!entries.length) return {}
  return {
    backgroundColor: 'transparent',
    tooltip: { backgroundColor: '#fff', borderColor: '#e4e7ed', textStyle: { color: '#303133' } },
    grid: { left: 16, right: 24, top: 8, bottom: 8, containLabel: true },
    xAxis: { type: 'value', splitLine: { lineStyle: { color: '#f0f0f0' } }, axisLabel: { color: '#909399', fontSize: 10 } },
    yAxis: { type: 'category', data: entries.map(e => e[0]), axisLabel: { color: '#606266', fontSize: 11 } },
    series: [{
      type: 'bar',
      data: entries.map(e => e[1]),
      itemStyle: {
        color: (params) => {
          const alpha = 0.4 + 0.6 * (1 - params.dataIndex / entries.length)
          return `rgba(64, 158, 255, ${alpha})`
        }
      },
      barMaxWidth: 20,
    }]
  }
})
</script>

<style scoped>
.tab-bar {
  display: flex;
  gap: 4px;
  margin-bottom: 20px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 4px;
  width: fit-content;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 20px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: #606266;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.tab-btn:hover { color: #303133; background: #f5f7fa; }
.tab-btn.active { background: #ecf5ff; color: #409eff; font-weight: 600; }

.tab-icon { font-size: 14px; }

.chart-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.card-header {
  padding: 14px 20px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.bottom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.metrics-table-wrap { overflow-x: auto; }

.metrics-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.metrics-table th {
  padding: 10px 12px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
  border-bottom: 1px solid #e4e7ed;
  background: #fafafa;
}
.metrics-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #f0f0f0;
  color: #303133;
}
.metrics-table tr:last-child td { border-bottom: none; }
.metrics-table tr:hover td { background: #f5f7fa; }

.model-name { font-weight: 600; font-size: 13px; color: #303133; }
.mono { font-family: monospace; font-size: 12px; color: #606266; }
.good { color: #67c23a !important; }
.empty { text-align: center; color: #909399; font-size: 13px; padding: 32px; }
</style>
