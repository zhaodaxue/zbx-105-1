<template>
  <div>
    <el-card shadow="never" class="stats-card">
      <template #header>
        <div class="card-header">
          <span class="title">当日各区域已批千瓦合计</span>
          <div class="actions">
            <el-date-picker
              v-model="targetDate"
              type="date"
              placeholder="选择日期"
              value-format="YYYY-MM-DD"
              style="width: 180px; margin-right: 12px;"
              :clearable="false"
              @change="loadStats"
            />
            <el-button type="primary" :icon="Download" @click="doExport">
              导出 CSV 摘要
            </el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="16" style="margin-bottom: 24px">
        <el-col :span="8">
          <div class="summary-card blue">
            <div class="s-label">统计日期</div>
            <div class="s-value date">{{ targetDate }}</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="summary-card green">
            <div class="s-label">已批准申报数</div>
            <div class="s-value">{{ data?.grand_total_count || 0 }} 单</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="summary-card orange">
            <div class="s-label">千瓦合计</div>
            <div class="s-value">{{ (data?.grand_total_kw || 0).toFixed(1) }} kW</div>
          </div>
        </el-col>
      </el-row>

      <el-table v-loading="loading" :data="data?.areas || []" style="width: 100%" border stripe>
        <el-table-column type="index" label="序号" width="70" align="center" />
        <el-table-column prop="stall_area" label="区域" width="220">
          <template #default="{ row }">
            <span class="area-name">📍 {{ row.stall_area }}</span>
          </template>
        </el-table-column>
        <el-table-column label="已批申报数" width="180" align="center">
          <template #default="{ row }">
            <el-tag type="primary" effect="light">{{ row.count }} 单</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="千瓦合计 (kW)" align="center">
          <template #default="{ row }">
            <span class="kw">{{ row.total_kw.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="占比" width="220">
          <template #default="{ row }">
            <el-progress
              :percentage="percent(row.total_kw)"
              :color="progressColor"
              :stroke-width="14"
              :text-inside="true"
            />
          </template>
        </el-table-column>
      </el-table>

      <el-empty
        v-if="!loading && (!data?.areas || data.areas.length === 0)"
        description="当日暂无已批准的用电申报"
        :image-size="120"
        style="padding: 60px 0"
      />
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { getDailyStatsApi, exportCsvApi } from '@/api'

const loading = ref(false)
const data = ref(null)
const targetDate = ref(dayjs().format('YYYY-MM-DD'))

const loadStats = async () => {
  loading.value = true
  try {
    data.value = await getDailyStatsApi({ target_date: targetDate.value })
  } catch (e) {
  } finally {
    loading.value = false
  }
}
onMounted(loadStats)

const percent = (kw) => {
  const total = data.value?.grand_total_kw || 0
  if (total <= 0) return 0
  return Math.round((kw / total) * 100)
}
const progressColor = [
  { color: '#67c23a', percentage: 20 },
  { color: '#409eff', percentage: 40 },
  { color: '#e6a23c', percentage: 70 },
  { color: '#f56c6c', percentage: 100 },
]

const doExport = () => {
  try {
    exportCsvApi({ target_date: targetDate.value })
    ElMessage.success('CSV 导出任务已启动，请查看下载文件')
  } catch (e) {
    ElMessage.error('导出失败')
  }
}
</script>

<style scoped>
.stats-card { border-radius: 8px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 15px; font-weight: 600; }
.actions { display: flex; align-items: center; }
.summary-card {
  border-radius: 8px;
  padding: 20px 22px;
  background: #f5f7fa;
  border-left: 4px solid #409eff;
}
.summary-card.blue { border-left-color: #409eff; }
.summary-card.green { border-left-color: #67c23a; }
.summary-card.orange { border-left-color: #e6a23c; }
.s-label { font-size: 13px; color: #909399; margin-bottom: 8px; }
.s-value {
  font-size: 26px; font-weight: 700; color: #303133; line-height: 1.1;
}
.s-value.date { color: #409eff; }
.area-name { font-weight: 600; color: #303133; }
.kw { font-size: 20px; font-weight: 700; color: #e6a23c; }
</style>
