<template>
  <div>
    <el-card shadow="never" class="review-card">
      <template #header>
        <div class="card-header">
          <span class="title">待审核申报</span>
          <div class="tabs">
            <el-radio-group v-model="activeTab" size="default">
              <el-radio-button value="pending">待审核 ({{ pendingCount }})</el-radio-button>
              <el-radio-button value="all">全部 ({{ total }})</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="list" style="width: 100%" stripe>
        <el-table-column prop="id" label="编号" width="70" />
        <el-table-column prop="stall_area" label="区域" width="100" />
        <el-table-column prop="stall_number" label="摊位号" width="100" />
        <el-table-column prop="peak_kw" label="峰值(kW)" width="100" align="center">
          <template #default="{ row }"><b>{{ row.peak_kw.toFixed(1) }}</b></template>
        </el-table-column>
        <el-table-column label="用电时段" width="260">
          <template #default="{ row }">
            <div class="time">
              <div>{{ formatTime(row.start_time) }}</div>
              <div class="muted">至 {{ formatTime(row.end_time) }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="明火" width="70" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.has_open_flame" type="danger" size="small">是</el-tag>
            <span v-else class="muted">-</span>
          </template>
        </el-table-column>
        <el-table-column label="申请人" width="100" prop="applicant_name" />
        <el-table-column label="提交时间" width="150">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ statusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="170" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="goDetail(row.id)">查看</el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="success"
              link
              @click="openApprove(row)"
            >批准</el-button>
            <el-button
              v-if="row.status === 'pending'"
              type="danger"
              link
              @click="openReject(row)"
            >驳回</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          background
          layout="total, prev, pager, next, jumper"
          :total="total"
          :current-page="page"
          :page-size="pageSize"
          @current-change="handlePage"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="showApproveDialog"
      title="批准申报 - 分配电表编号"
      width="480px"
    >
      <el-descriptions v-if="currentRow" :column="2" border size="small" style="margin-bottom: 16px">
        <el-descriptions-item label="区域">{{ currentRow.stall_area }}</el-descriptions-item>
        <el-descriptions-item label="摊位">{{ currentRow.stall_number }}</el-descriptions-item>
        <el-descriptions-item label="峰值">{{ currentRow.peak_kw.toFixed(1) }} kW</el-descriptions-item>
        <el-descriptions-item label="申请人">{{ currentRow.applicant_name }}</el-descriptions-item>
      </el-descriptions>
      <el-form ref="approveFormRef" :model="approveForm" :rules="approveRules" label-width="90px">
        <el-form-item label="电表编号" prop="meter_number">
          <el-input v-model="approveForm.meter_number" placeholder="例：TM-A001" maxlength="50" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showApproveDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="doApprove">确认批准</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showRejectDialog"
      title="驳回申报 - 填写原因"
      width="480px"
    >
      <el-descriptions v-if="currentRow" :column="2" border size="small" style="margin-bottom: 16px">
        <el-descriptions-item label="区域">{{ currentRow.stall_area }}</el-descriptions-item>
        <el-descriptions-item label="摊位">{{ currentRow.stall_number }}</el-descriptions-item>
        <el-descriptions-item label="峰值">{{ currentRow.peak_kw.toFixed(1) }} kW</el-descriptions-item>
        <el-descriptions-item label="申请人">{{ currentRow.applicant_name }}</el-descriptions-item>
      </el-descriptions>
      <el-form ref="rejectFormRef" :model="rejectForm" :rules="rejectRules" label-width="90px">
        <el-form-item label="驳回原因" prop="reject_reason">
          <el-input
            v-model="rejectForm.reject_reason"
            type="textarea"
            :rows="4"
            placeholder="请填写驳回原因（如：峰值过高请分摊、时段冲突等）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRejectDialog = false">取消</el-button>
        <el-button type="danger" :loading="submitting" @click="doReject">确认驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref, reactive, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { listApplicationsApi, reviewApplicationApi } from '@/api'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const activeTab = ref('pending')

const allApplications = ref([])

const pendingCount = computed(() =>
  allApplications.value.filter((a) => a.status === 'pending').length
)

const statusTag = (s) => ({ pending: 'warning', approved: 'success', rejected: 'danger' }[s])
const statusText = (s) => ({ pending: '待审核', approved: '已批准', rejected: '已驳回' }[s])
const formatTime = (t) => (t ? dayjs(t).format('MM-DD HH:mm') : '-')

const load = async () => {
  loading.value = true
  try {
    const res = await listApplicationsApi({
      status: activeTab.value === 'pending' ? 'pending' : undefined,
      limit: 500,
    })
    const all = res.items || []
    allApplications.value = all
    total.value = res.total
    const start = (page.value - 1) * pageSize.value
    list.value = all.slice(start, start + pageSize.value)
  } finally {
    loading.value = false
  }
}
onMounted(load)

watch(activeTab, () => {
  page.value = 1
  load()
})

const handlePage = (p) => {
  page.value = p
  load()
}
const goDetail = (id) => router.push(`/applications/${id}`)

const currentRow = ref(null)
const showApproveDialog = ref(false)
const showRejectDialog = ref(false)
const submitting = ref(false)
const approveFormRef = ref(null)
const rejectFormRef = ref(null)

const approveForm = reactive({ meter_number: '' })
const rejectForm = reactive({ reject_reason: '' })
const approveRules = {
  meter_number: [{ required: true, message: '请输入电表编号', trigger: 'blur' }],
}
const rejectRules = {
  reject_reason: [{ required: true, message: '请填写驳回原因', trigger: 'blur' }],
}

const openApprove = (row) => {
  currentRow.value = row
  approveForm.meter_number = `TM-${row.stall_area[0]}${String(row.id).padStart(3, '0')}`
  showApproveDialog.value = true
}
const openReject = (row) => {
  currentRow.value = row
  rejectForm.reject_reason = ''
  showRejectDialog.value = true
}

const doApprove = async () => {
  await approveFormRef.value?.validate()
  submitting.value = true
  try {
    await reviewApplicationApi(currentRow.value.id, {
      status: 'approved',
      meter_number: approveForm.meter_number.trim(),
    })
    ElMessage.success(`已批准，电表 ${approveForm.meter_number}`)
    showApproveDialog.value = false
    load()
  } catch (e) {
  } finally {
    submitting.value = false
  }
}
const doReject = async () => {
  await rejectFormRef.value?.validate()
  await ElMessageBox.confirm(
    '确认驳回该申报？驳回后摊主需重新提交。',
    '提示',
    { type: 'warning', confirmButtonText: '确认驳回' }
  )
  submitting.value = true
  try {
    await reviewApplicationApi(currentRow.value.id, {
      status: 'rejected',
      reject_reason: rejectForm.reject_reason.trim(),
    })
    ElMessage.success('已驳回')
    showRejectDialog.value = false
    load()
  } catch (e) {
  } finally {
    submitting.value = false
  }
}

const openFromQuery = () => {
  if (route.query.id) {
    router.push(`/applications/${route.query.id}`)
  }
}
onMounted(openFromQuery)
</script>

<style scoped>
.review-card { border-radius: 8px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 15px; font-weight: 600; }
.time { font-size: 13px; line-height: 1.5; }
.muted { color: #909399; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>
