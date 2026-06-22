<template>
  <div>
    <el-card shadow="never" class="filter-card">
      <el-form :inline="true" :model="filters" @submit.prevent>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部" clearable style="width: 140px">
            <el-option label="待审核" value="pending" />
            <el-option label="已批准" value="approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="区域">
          <el-input v-model="filters.stall_area" placeholder="按区域筛选" clearable style="width: 160px" />
        </el-form-item>
        <el-form-item label="摊位号">
          <el-input v-model="filters.stall_number" placeholder="按摊位号" clearable style="width: 140px" />
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 280px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
        <el-form-item style="margin-left: auto">
          <el-button v-if="userStore.isVendor" type="success" :icon="Plus" @click="$router.push('/applications/create')">
            新建申报
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="table-card">
      <el-table v-loading="loading" :data="list" style="width: 100%" :stripe="true">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="stall_area" label="区域" width="110" />
        <el-table-column prop="stall_number" label="摊位号" width="110" />
        <el-table-column prop="peak_kw" label="峰值(kW)" width="100" align="center">
          <template #default="{ row }"><b>{{ row.peak_kw.toFixed(1) }}</b></template>
        </el-table-column>
        <el-table-column label="用电时段" width="320">
          <template #default="{ row }">
            <div class="time-range">
              <span>{{ formatTime(row.start_time) }}</span>
              <el-icon><Right /></el-icon>
              <span>{{ formatTime(row.end_time) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="明火" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.has_open_flame" type="danger" size="small">是</el-tag>
            <span v-else class="muted">否</span>
          </template>
        </el-table-column>
        <el-table-column label="电表编号" width="140">
          <template #default="{ row }">
            <span v-if="row.meter_number" class="meter-no">{{ row.meter_number }}</span>
            <span v-else class="muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="!userStore.isVendor" label="申请人" width="100" prop="applicant_name" />
        <el-table-column label="提交时间" width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="goDetail(row.id)">查看</el-button>
            <el-button
              v-if="userStore.isElectrician && row.status === 'pending'"
              type="warning"
              link
              @click="goReview(row.id)"
            >审核</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          background
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          :current-page="page"
          :page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          @current-change="handlePage"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Right } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import { listApplicationsApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)

const filters = reactive({
  status: '',
  stall_area: '',
  stall_number: '',
  dateRange: [],
})

const statusTag = (s) => ({ pending: 'warning', approved: 'success', rejected: 'danger' }[s])
const statusText = (s) => ({ pending: '待审核', approved: '已批准', rejected: '已驳回' }[s])
const formatTime = (t) => (t ? dayjs(t).format('YYYY-MM-DD HH:mm') : '-')

const buildParams = () => ({
  status: filters.status || undefined,
  stall_area: filters.stall_area || undefined,
  stall_number: filters.stall_number || undefined,
  start_date: filters.dateRange?.[0],
  end_date: filters.dateRange?.[1],
  skip: (page.value - 1) * pageSize.value,
  limit: pageSize.value,
})

const loadList = async () => {
  loading.value = true
  try {
    const res = await listApplicationsApi(buildParams())
    list.value = res.items
    total.value = res.total
  } catch (e) {
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  loadList()
}
const resetFilters = () => {
  filters.status = ''
  filters.stall_area = ''
  filters.stall_number = ''
  filters.dateRange = []
  handleSearch()
}
const handlePage = (p) => {
  page.value = p
  loadList()
}
const handleSizeChange = (s) => {
  pageSize.value = s
  page.value = 1
  loadList()
}
const goDetail = (id) => router.push(`/applications/${id}`)
const goReview = (id) => router.push({ path: '/review', query: { id } })

onMounted(loadList)
</script>

<style scoped>
.filter-card { margin-bottom: 16px; border-radius: 8px; }
.table-card { border-radius: 8px; }
.time-range {
  display: inline-flex; align-items: center; gap: 6px; font-size: 13px;
  color: #606266;
}
.meter-no {
  font-family: Menlo, Monaco, Consolas, monospace;
  color: #409eff;
  font-weight: 600;
}
.muted { color: #c0c4cc; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>
