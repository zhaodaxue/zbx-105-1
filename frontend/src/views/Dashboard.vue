<template>
  <div class="dashboard">
    <el-row :gutter="16">
      <el-col :span="6" v-for="card in statCards" :key="card.key">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-inner" :class="card.color">
            <div class="stat-left">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
            <el-icon class="stat-icon"><component :is="card.icon" /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="content-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">快捷入口</span>
        </div>
      </template>
      <el-row :gutter="12">
        <el-col :span="6" v-if="userStore.isVendor">
          <router-link to="/applications/create">
            <div class="shortcut-card">
              <el-icon class="shortcut-icon" color="#67c23a"><Edit /></el-icon>
              <div class="shortcut-title">提交用电申报</div>
              <div class="shortcut-desc">填写摊位信息和用电需求</div>
            </div>
          </router-link>
        </el-col>
        <el-col :span="6">
          <router-link to="/applications">
            <div class="shortcut-card">
              <el-icon class="shortcut-icon" color="#409eff"><Document /></el-icon>
              <div class="shortcut-title">我的申报记录</div>
              <div class="shortcut-desc">查看所有申报状态和详情</div>
            </div>
          </router-link>
        </el-col>
        <el-col :span="6" v-if="userStore.isElectrician">
          <router-link to="/review">
            <div class="shortcut-card">
              <el-icon class="shortcut-icon" color="#e6a23c"><Check /></el-icon>
              <div class="shortcut-title">待审核申报</div>
              <div class="shortcut-desc">批准或驳回待处理的申请</div>
            </div>
          </router-link>
        </el-col>
        <el-col :span="6" v-if="userStore.isPlanner || userStore.isElectrician">
          <router-link to="/stats">
            <div class="shortcut-card">
              <el-icon class="shortcut-icon" color="#909399"><DataAnalysis /></el-icon>
              <div class="shortcut-title">统计摘要</div>
              <div class="shortcut-desc">查看各区域用电合计并导出</div>
            </div>
          </router-link>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="content-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">最近申报动态</span>
          <el-button text type="primary" @click="$router.push('/applications')">查看全部 →</el-button>
        </div>
      </template>
      <el-table v-loading="loading" :data="recentList" size="default" style="width: 100%">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="stall_area" label="区域" width="120" />
        <el-table-column prop="stall_number" label="摊位号" width="120" />
        <el-table-column prop="peak_kw" label="峰值(kW)" width="110">
          <template #default="{ row }">
            <b>{{ row.peak_kw.toFixed(1) }}</b>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="申报人" width="120" prop="applicant_name" />
        <el-table-column label="提交时间" width="180">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" link @click="goDetail(row.id)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { listApplicationsApi } from '@/api'
import { useUserStore } from '@/stores/user'
import dayjs from 'dayjs'
import {
  Document, Check, DataAnalysis, Edit, Clock, WarningFilled, CircleCheckFilled, Warning,
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const applications = ref([])

const loadApplications = async () => {
  loading.value = true
  try {
    const res = await listApplicationsApi({ limit: 10 })
    applications.value = res.items || []
  } finally {
    loading.value = false
  }
}

onMounted(loadApplications)

const recentList = computed(() => applications.value.slice(0, 8))

const pendingCount = computed(() => applications.value.filter(a => a.status === 'pending').length)
const approvedCount = computed(() => applications.value.filter(a => a.status === 'approved').length)
const rejectedCount = computed(() => applications.value.filter(a => a.status === 'rejected').length)
const totalKw = computed(() =>
  applications.value
    .filter(a => a.status === 'approved')
    .reduce((sum, a) => sum + a.peak_kw, 0)
    .toFixed(1)
)

const statCards = computed(() => {
  const cards = [
    { key: 'pending', label: '待审核', value: pendingCount.value, color: 'orange', icon: Clock },
    { key: 'approved', label: '已批准', value: approvedCount.value, color: 'green', icon: CircleCheckFilled },
  ]
  if (userStore.isPlanner || userStore.isElectrician) {
    cards.push({ key: 'kw', label: '已批千瓦合计', value: totalKw.value, color: 'blue', icon: DataAnalysis })
  }
  cards.push({ key: 'rejected', label: '已驳回', value: rejectedCount.value, color: 'red', icon: WarningFilled })
  return cards
})

const statusTag = (s) => ({ pending: 'warning', approved: 'success', rejected: 'danger' }[s])
const statusText = (s) => ({ pending: '待审核', approved: '已批准', rejected: '已驳回' }[s])
const formatTime = (t) => (t ? dayjs(t).format('YYYY-MM-DD HH:mm') : '-')
const goDetail = (id) => router.push(`/applications/${id}`)
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 16px; }
.stat-card { border-radius: 8px; }
.stat-inner {
  display: flex; justify-content: space-between; align-items: center;
  padding: 4px;
}
.stat-value { font-size: 30px; font-weight: 700; line-height: 1; margin-bottom: 8px; }
.stat-label { font-size: 13px; color: #606266; }
.stat-icon { font-size: 52px; opacity: 0.18; }
.stat-inner.orange .stat-value { color: #e6a23c; }
.stat-inner.green .stat-value { color: #67c23a; }
.stat-inner.blue .stat-value { color: #409eff; }
.stat-inner.red .stat-value { color: #f56c6c; }
.content-card { border-radius: 8px; }
.card-header {
  display: flex; justify-content: space-between; align-items: center;
}
.title { font-size: 15px; font-weight: 600; }
.shortcut-card {
  background: #fafbfc;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 20px 18px;
  transition: all 0.2s;
  cursor: pointer;
  color: inherit;
  text-decoration: none;
  display: block;
}
.shortcut-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.12);
  transform: translateY(-2px);
}
.shortcut-icon { font-size: 30px; margin-bottom: 10px; }
.shortcut-title { font-size: 15px; font-weight: 600; color: #303133; margin-bottom: 4px; }
.shortcut-desc { font-size: 12px; color: #909399; }
:deep(a) { text-decoration: none; color: inherit; display: block; }
</style>
