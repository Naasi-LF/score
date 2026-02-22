<template>
  <div>
    <h2 class="page-title">数据概览</h2>
    <div class="stat-grid">
      <div v-for="card in statCards" :key="card.label" class="stat-card">
        <div class="stat-icon">{{ card.icon }}</div>
        <div class="stat-body">
          <div class="stat-value">{{ card.value }}</div>
          <div class="stat-label">{{ card.label }}</div>
        </div>
      </div>
    </div>
    <div class="chart-grid">
      <div class="chart-card">
        <div class="chart-header">成绩分布</div>
        <v-chart :option="pieOption" style="height:300px" autoresize />
      </div>
      <div class="chart-card">
        <div class="chart-header">成绩区间柱状图</div>
        <v-chart :option="barOption" style="height:300px" autoresize />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import api from '../api/index.js'

use([PieChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

const overview = ref({})
const distribution = ref({})

onMounted(async () => {
  const [ov, dist] = await Promise.all([
    api.get('/analytics/overview'),
    api.get('/analytics/distribution'),
  ])
  overview.value = ov.data
  distribution.value = dist.data
})

const statCards = computed(() => [
  { label: '学生总数',     value: overview.value.total_students ?? '—', icon: '👥' },
  { label: '期中平均分 G1', value: overview.value.avg_g1 ?? '—',         icon: '📝' },
  { label: '期末平均分 G2', value: overview.value.avg_g2 ?? '—',         icon: '📊' },
  { label: '高风险人数',   value: overview.value.high_risk_count ?? '—', icon: '⚠️' },
])

const COLORS = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399']

const pieOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'item', formatter: '{b}: {c} 人 ({d}%)' },
  legend: { bottom: 0, textStyle: { color: '#606266', fontSize: 12 } },
  series: [{
    type: 'pie',
    radius: ['38%', '65%'],
    center: ['50%', '45%'],
    itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
    label: { show: false },
    data: Object.entries(distribution.value).map(([name, value], i) => ({
      name, value, itemStyle: { color: COLORS[i % COLORS.length] }
    }))
  }]
}))

const barOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 40, right: 16, top: 16, bottom: 40 },
  xAxis: {
    type: 'category',
    data: Object.keys(distribution.value),
    axisLine: { lineStyle: { color: '#dcdfe6' } },
    axisLabel: { color: '#606266', fontSize: 12 },
  },
  yAxis: {
    type: 'value',
    axisLine: { show: false },
    splitLine: { lineStyle: { color: '#f0f0f0' } },
    axisLabel: { color: '#909399', fontSize: 11 },
  },
  series: [{
    type: 'bar',
    barMaxWidth: 48,
    data: Object.values(distribution.value),
    itemStyle: {
      color: '#409eff',
      borderRadius: [4, 4, 0, 0],
    },
  }]
}))
</script>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.stat-icon { font-size: 28px; }

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.chart-card {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.chart-header {
  padding: 14px 20px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}
</style>
