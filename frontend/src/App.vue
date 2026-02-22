<template>
  <router-view />
</template>

<style>
:root {
  --bg-base: #f0f2f5;
  --bg-surface: #ffffff;
  --bg-card: #ffffff;
  --border: #e4e7ed;
  --border-light: #f0f0f0;
  --accent: #409eff;
  --accent-dim: rgba(64,158,255,0.1);
  --accent-dark: #337ecc;
  --success: #67c23a;
  --danger: #f56c6c;
  --warning: #e6a23c;
  --text-primary: #303133;
  --text-secondary: #606266;
  --text-muted: #909399;
  --shadow-sm: 0 1px 4px rgba(0,0,0,0.08);
  --shadow-md: 0 2px 12px rgba(0,0,0,0.1);
  --font-body: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, #app {
  height: 100%;
  background: var(--bg-base);
  color: var(--text-primary);
  font-family: var(--font-body);
  font-size: 14px;
  -webkit-font-smoothing: antialiased;
}

/* Element Plus overrides */
.el-card {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  box-shadow: var(--shadow-sm) !important;
}
.el-card__header {
  border-bottom: 1px solid var(--border-light) !important;
  font-weight: 600 !important;
  color: var(--text-primary) !important;
  padding: 14px 20px !important;
}
.el-button--primary {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
}
.el-button--primary:hover {
  background: var(--accent-dark) !important;
  border-color: var(--accent-dark) !important;
}
.el-table {
  background: transparent !important;
}
.el-table th {
  background: #fafafa !important;
  color: var(--text-secondary) !important;
  font-weight: 600 !important;
}
.el-table td, .el-table th {
  border-bottom: 1px solid var(--border-light) !important;
}
.el-input__wrapper {
  box-shadow: 0 0 0 1px var(--border) inset !important;
}
.el-input__wrapper:hover {
  box-shadow: 0 0 0 1px var(--accent) inset !important;
}
.el-select .el-input__wrapper {
  box-shadow: 0 0 0 1px var(--border) inset !important;
}
.el-pagination {
  color: var(--text-secondary) !important;
}

.page-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.page-title::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 20px;
  background: var(--accent);
  border-radius: 2px;
}
</style>
