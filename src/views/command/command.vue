<script setup>
import { ref, onMounted, watch } from 'vue';
import { GetCommandListApi } from '../../api/users';
import { useRoute } from 'vue-router';

const route = useRoute()
let machine_name = ref('');
let userid = ref(localStorage.getItem('Id'))

onMounted(() => {
  machine_name.value = route.query.machineName || '';
  getCommandList();
})

const getCommandList = async () => {
  const machines = machine_name.value;
  const userId = userid.value;
  const data = { machines, userId }
  const result = await GetCommandListApi(data);
  if (result && result.code === 1) {
    if (result.data && result.data.rows && result.data.rows.length > 0) {
      tableData.value = result.data.rows;
      return;
    }
    tableData.value = []
  } else {
    tableData.value = []
  }
}

watch(() => route.query.machineName, (newValue) => {
  machine_name.value = newValue || '';
  getCommandList();
}, { immediate: true });

const tableData = ref([])

const statusClass = (code) => {
  if (!code) return ''
  if (code.includes('成功')) return 'status-ok'
  if (code.includes('失败') || code.includes('错误')) return 'status-fail'
  return 'status-pending'
}
</script>

<template>
  <div class="cmd-root">

    <div class="page-header">
      <div class="page-header-left">
        <div class="page-title-icon">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <rect x="2" y="3" width="12" height="10" rx="2" stroke="white" stroke-width="1.4"/>
            <path d="M5 8h6M8 5v6" stroke="white" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
        </div>
        <div>
          <div class="page-title">命令列表</div>
          <div class="page-sub">{{ machine_name ? '设备：' + machine_name : '请从菜单选择设备' }} · 共 {{ tableData.length }} 条记录</div>
        </div>
      </div>
    </div>

    <div class="table-wrap" v-if="tableData.length > 0">
      <el-table
        :data="tableData"
        style="width:100%; border-radius:14px; overflow:hidden;"
        :header-cell-style="{ background:'#FFF5F0', color:'#8A4030', fontWeight:'600', fontSize:'13px', padding:'14px 0', borderBottom:'1px solid rgba(255,160,120,0.2)' }"
        :cell-style="{ fontSize:'13px', color:'#3A2010', padding:'13px 0', borderBottom:'1px solid rgba(255,160,120,0.08)' }"
      >
        <el-table-column type="index" label="#" width="60" align="center"/>
        <el-table-column prop="commandName" label="命令名称" min-width="200" align="left">
          <template #default="{ row }">
            <span class="cmd-name">{{ row.commandName }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="commandCode" label="执行状态" min-width="150" align="center">
          <template #default="{ row }">
            <span class="status-badge" :class="statusClass(row.commandCode)">{{ row.commandCode || '未知' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="time" label="执行时间" min-width="200" align="center">
          <template #default="{ row }">
            <span class="time-text">{{ row.time }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="empty-state" v-else>
      <div class="empty-icon">📟</div>
      <div class="empty-title">暂无命令记录</div>
      <div class="empty-sub">{{ machine_name ? '该设备暂未执行任何命令' : '请先在左侧「命令查询」菜单中选择一台设备' }}</div>
    </div>

  </div>
</template>

<style scoped>
.cmd-root {
  width: 100%; height: 100%;
  padding: 20px 24px; box-sizing: border-box;
  display: flex; flex-direction: column; gap: 16px;
  overflow: hidden; position: relative;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

.page-header { display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
.page-header-left { display: flex; align-items: center; gap: 12px; }
.page-title-icon {
  width: 40px; height: 40px; border-radius: 12px;
  background: linear-gradient(135deg, #FF9A76, #FF6040);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(255,96,64,0.28); flex-shrink: 0;
}
.page-title { font-size: 18px; font-weight: 700; color: #3A2010; letter-spacing: 0.01em; }
.page-sub { font-size: 12px; color: #B09080; margin-top: 2px; }

.table-wrap {
  flex: 1; overflow-y: auto; border-radius: 14px;
  border: 1px solid rgba(255,160,120,0.15);
  box-shadow: 0 4px 20px rgba(200,90,50,0.06); background: #FFFFFF;
}
.table-wrap::-webkit-scrollbar { width: 4px; }
.table-wrap::-webkit-scrollbar-thumb { background: rgba(255,160,120,0.3); border-radius: 4px; }

.cmd-name { font-weight: 600; color: #3A2010; }
.time-text { color: #7A5040; font-size: 12.5px; }

.status-badge {
  font-size: 11px; font-weight: 600;
  border-radius: 100px; padding: 3px 10px;
  border: 1px solid transparent;
}
.status-ok { background: #F0F7EE; color: #4A7A40; border-color: rgba(80,160,60,0.2); }
.status-fail { background: #FFF0EE; color: #C03030; border-color: rgba(200,60,40,0.2); }
.status-pending { background: #FFF8E8; color: #A06020; border-color: rgba(200,140,40,0.2); }

.empty-state {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 8px;
  background: #FFFFFF; border-radius: 14px;
  border: 1px solid rgba(255,160,120,0.15);
  box-shadow: 0 4px 20px rgba(200,90,50,0.06);
}
.empty-icon { font-size: 40px; }
.empty-title { font-size: 16px; font-weight: 700; color: #5A3020; }
.empty-sub { font-size: 13px; color: #B09080; text-align: center; max-width: 300px; }
</style>
