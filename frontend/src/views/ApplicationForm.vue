<template>
  <div>
    <el-card shadow="never" class="form-card">
      <template #header>
        <div class="card-header">
          <span class="title">提交用电申报</span>
          <el-button link type="primary" @click="$router.back()">← 返回列表</el-button>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="130px"
        style="max-width: 720px; margin: 0 auto;"
      >
        <el-divider content-position="left">摊位信息</el-divider>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="摊位所属区域" prop="stall_area">
              <el-select v-model="form.stall_area" placeholder="请选择区域" style="width: 100%">
                <el-option label="A区 - 主街东段" value="A区" />
                <el-option label="B区 - 主街西段" value="B区" />
                <el-option label="C区 - 美食广场" value="C区" />
                <el-option label="D区 - 手作市集" value="D区" />
                <el-option label="E区 - 儿童乐园" value="E区" />
                <el-option label="F区 - 农产品展销" value="F区" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="摊位编号" prop="stall_number">
              <el-input v-model="form.stall_number" placeholder="例：A-01" maxlength="20" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">用电需求</el-divider>
        <el-form-item label="预估峰值功率" prop="peak_kw">
          <el-input-number
            v-model="form.peak_kw"
            :min="0.1"
            :max="100"
            :step="0.5"
            :precision="1"
            style="width: 200px"
          />
          <span class="unit">千瓦 (kW)</span>
          <div class="hint">提示：普通照明约0.5kW，电磁炉约2-3kW，冰柜约1-2kW</div>
        </el-form-item>

        <el-form-item label="用电时段" prop="timeRange">
          <el-date-picker
            v-model="form.timeRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
            format="YYYY-MM-DD HH:mm"
            style="width: 420px"
          />
        </el-form-item>

        <el-form-item label="是否使用明火厨灶" prop="has_open_flame">
          <el-radio-group v-model="form.has_open_flame">
            <el-radio :label="false">否</el-radio>
            <el-radio :label="true">是（需特别注意防火）</el-radio>
          </el-radio-group>
          <div v-if="form.has_open_flame" class="warn-hint">
            <el-icon color="#e6a23c"><WarningFilled /></el-icon>
            使用明火需经消防安全检查，请配合现场管理人员
          </div>
        </el-form-item>

        <el-divider />

        <el-form-item>
          <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
            提交申报
          </el-button>
          <el-button size="large" @click="$router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { WarningFilled } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { createApplicationApi } from '@/api'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)

const form = reactive({
  stall_area: '',
  stall_number: '',
  peak_kw: 1,
  timeRange: [],
  has_open_flame: false,
})

const rules = {
  stall_area: [{ required: true, message: '请选择摊位区域', trigger: 'change' }],
  stall_number: [
    { required: true, message: '请输入摊位编号', trigger: 'blur' },
    { min: 2, max: 20, message: '长度 2-20 个字符', trigger: 'blur' },
  ],
  peak_kw: [
    { required: true, message: '请输入峰值功率', trigger: 'blur' },
    { type: 'number', min: 0.1, message: '功率必须大于 0', trigger: 'blur' },
  ],
  timeRange: [
    {
      required: true,
      validator: (_r, v, cb) => {
        if (!v || v.length !== 2) return cb(new Error('请选择用电时段'))
        const [s, e] = v
        if (dayjs(e).isBefore(dayjs(s))) return cb(new Error('结束时间必须晚于开始时间'))
        cb()
      },
      trigger: 'change',
    },
  ],
}

const handleSubmit = async () => {
  await formRef.value?.validate()
  await ElMessageBox.confirm(
    `确认提交此用电申报？<br/>区域：${form.stall_area}｜摊位：${form.stall_number}<br/>峰值：${form.peak_kw} kW`,
    '提示',
    { dangerouslyUseHTMLString: true, confirmButtonText: '确认提交', type: 'info' }
  )
  submitting.value = true
  try {
    const [start, end] = form.timeRange
    const res = await createApplicationApi({
      stall_area: form.stall_area,
      stall_number: form.stall_number,
      peak_kw: form.peak_kw,
      start_time: start,
      end_time: end,
      has_open_flame: form.has_open_flame,
    })
    ElMessage.success('申报提交成功，等待电工审核')
    router.push(`/applications/${res.id}`)
  } catch (e) {
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.form-card { border-radius: 8px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 15px; font-weight: 600; }
.unit { margin-left: 12px; color: #909399; font-size: 13px; }
.hint { margin-top: 6px; color: #909399; font-size: 12px; }
.warn-hint {
  margin-top: 8px; padding: 8px 12px;
  background: #fdf6ec; border: 1px solid #faecd8;
  color: #e6a23c; border-radius: 4px; font-size: 13px;
  display: flex; align-items: center; gap: 6px;
}
</style>
