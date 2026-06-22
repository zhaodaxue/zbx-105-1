<template>
  <div>
    <el-card shadow="never" class="detail-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button link type="primary" @click="$router.back()">← 返回</el-button>
            <span class="title">申报详情 #{{ data?.id }}</span>
            <el-tag :type="statusTag(data?.status)" size="large" effect="dark" style="margin-left: 12px">
              {{ statusText(data?.status) }}
            </el-tag>
          </div>
          <div v-if="canReview" class="header-right">
            <el-button type="warning" @click="showReviewDialog = true" :icon="Check">
              审核
            </el-button>
          </div>
        </div>
      </template>

      <el-descriptions :column="2" border v-if="data">
        <el-descriptions-item label="摊位区域">{{ data.stall_area }}</el-descriptions-item>
        <el-descriptions-item label="摊位编号">{{ data.stall_number }}</el-descriptions-item>
        <el-descriptions-item label="预估峰值功率">
          <span class="kw">{{ data.peak_kw.toFixed(1) }} kW</span>
        </el-descriptions-item>
        <el-descriptions-item label="使用明火厨灶">
          <el-tag v-if="data.has_open_flame" type="danger" size="small">是</el-tag>
          <span v-else>否</span>
        </el-descriptions-item>
        <el-descriptions-item label="用电开始时间" :span="1">
          {{ formatTime(data.start_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="用电结束时间" :span="1">
          {{ formatTime(data.end_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="申请人">{{ data.applicant_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ formatTime(data.created_at) }}</el-descriptions-item>
      </el-descriptions>

      <el-divider v-if="data" />

      <el-descriptions :column="2" border v-if="data">
        <template v-if="data.status === 'approved'">
          <el-descriptions-item label="电表编号">
            <span class="meter-no">{{ data.meter_number }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="审核人">{{ data.reviewer_name }}</el-descriptions-item>
        </template>
        <template v-else-if="data.status === 'rejected'">
          <el-descriptions-item label="驳回原因" :span="2">
            <div class="reject-reason">{{ data.reject_reason }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="审核人">{{ data.reviewer_name }}</el-descriptions-item>
        </template>
        <el-descriptions-item v-if="data.reviewed_at" label="审核时间">
          {{ formatTime(data.reviewed_at) }}
        </el-descriptions-item>
        <el-descriptions-item v-else label="审核状态">
          <span class="muted">尚未审核</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-dialog
      v-model="showReviewDialog"
      title="审核申报"
      width="540px"
      :close-on-click-modal="false"
    >
      <el-form ref="reviewFormRef" :model="reviewForm" :rules="reviewRules" label-width="110px">
        <el-alert
          title="审批前请仔细核对摊位号、峰值功率、用电时段和明火使用情况"
          type="info"
          :closable="false"
          style="margin-bottom: 16px;"
        />
        <el-form-item label="审核结果" prop="status">
          <el-radio-group v-model="reviewForm.status">
            <el-radio-button value="approved">批准</el-radio-button>
            <el-radio-button value="rejected">驳回</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item
          v-if="reviewForm.status === 'approved'"
          label="电表编号"
          prop="meter_number"
        >
          <el-input v-model="reviewForm.meter_number" placeholder="例：TM-A001" maxlength="50" />
          <div class="hint">建议格式：TM-区域+流水号，如 TM-C012</div>
        </el-form-item>
        <el-form-item
          v-if="reviewForm.status === 'rejected'"
          label="驳回原因"
          prop="reject_reason"
        >
          <el-input
            v-model="reviewForm.reject_reason"
            type="textarea"
            :rows="4"
            placeholder="请填写驳回原因，便于摊主修改后重新提交"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showReviewDialog = false">取消</el-button>
        <el-button type="primary" :loading="reviewing" @click="submitReview">
          确认审核
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { getApplicationApi, reviewApplicationApi } from '@/api'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)
const data = ref(null)

const id = computed(() => Number(route.params.id))
const canReview = computed(
  () => userStore.isElectrician && data.value?.status === 'pending'
)

const load = async () => {
  loading.value = true
  try {
    data.value = await getApplicationApi(id.value)
  } finally {
    loading.value = false
  }
}
onMounted(load)

const statusTag = (s) => ({ pending: 'warning', approved: 'success', rejected: 'danger' }[s])
const statusText = (s) => ({ pending: '待审核', approved: '已批准', rejected: '已驳回' }[s])
const formatTime = (t) => (t ? dayjs(t).format('YYYY-MM-DD HH:mm') : '-')

const showReviewDialog = ref(false)
const reviewing = ref(false)
const reviewFormRef = ref(null)
const reviewForm = reactive({
  status: 'approved',
  meter_number: '',
  reject_reason: '',
})
const reviewRules = {
  status: [{ required: true, message: '请选择审核结果', trigger: 'change' }],
  meter_number: [
    {
      validator: (_r, v, cb) => {
        if (reviewForm.status === 'approved' && (!v || !v.trim())) {
          return cb(new Error('批准必须分配电表编号'))
        }
        cb()
      },
      trigger: 'blur',
    },
  ],
  reject_reason: [
    {
      validator: (_r, v, cb) => {
        if (reviewForm.status === 'rejected' && (!v || !v.trim())) {
          return cb(new Error('驳回必须填写原因'))
        }
        cb()
      },
      trigger: 'blur',
    },
  ],
}

const submitReview = async () => {
  await reviewFormRef.value?.validate()
  reviewing.value = true
  try {
    const payload = { status: reviewForm.status }
    if (reviewForm.status === 'approved') {
      payload.meter_number = reviewForm.meter_number.trim()
    } else {
      payload.reject_reason = reviewForm.reject_reason.trim()
    }
    await reviewApplicationApi(id.value, payload)
    ElMessage.success(reviewForm.status === 'approved' ? '已批准并分配电表' : '已驳回')
    showReviewDialog.value = false
    load()
  } catch (e) {
  } finally {
    reviewing.value = false
  }
}
</script>

<style scoped>
.detail-card { border-radius: 8px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; }
.title { font-size: 15px; font-weight: 600; margin-left: 12px; }
.kw { font-size: 18px; font-weight: 700; color: #409eff; }
.meter-no {
  font-family: Menlo, Monaco, Consolas, monospace;
  font-weight: 600; color: #67c23a;
  padding: 2px 8px; background: #f0f9eb; border-radius: 4px;
}
.reject-reason {
  background: #fef0f0; color: #f56c6c;
  padding: 8px 12px; border-radius: 4px; line-height: 1.6;
}
.muted { color: #c0c4cc; }
.hint { margin-top: 6px; font-size: 12px; color: #909399; }
</style>
