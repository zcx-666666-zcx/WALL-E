<script setup>
import { ref, onMounted } from 'vue';
import { GetMachineListApi } from '@/api/users.js';
import { AddMachineApi } from '../../api/users';
import { DeleteMachinesApi } from '../../api/users';
import { UpdateMachineIpApi } from '../../api/users';
import { toast, confirm } from '../../utils/toast';

let haveNot = ref(true)
let add = ref(false)
let canadd = ref("添加")
let userid = ref(localStorage.getItem('Id'))
let MachinesInfo = ref({ machines: '', connectionId: '', robotIp: '', userId: userid.value })
let editingIpId = ref(null)
let editingIpValue = ref('')

onMounted(() => { getList() })

const getList = async () => {
    const result = await GetMachineListApi(userid.value);
    if (result && result.code === 1) {
        if (result.data?.rows?.length > 0) { tableData.value = result.data.rows; haveNot.value = false; }
        else { tableData.value = []; haveNot.value = true; }
    } else { toast.error("获取表格数据失败"); }
}

const AddMachine = async () => {
    if (!MachinesInfo.value.machines || !MachinesInfo.value.connectionId) { toast.warning("请输入完整内容"); return; }
    canadd.value = "添加中…";
    const result = await AddMachineApi(MachinesInfo.value);
    if (result?.code === 1) toast.success("添加设备成功"); else toast.error("添加设备失败");
    canadd.value = "添加"; getList(); close();
}

const deleteMachine = async (machines) => {
    if (!await confirm(`确定要删除设备「${machines}」吗？`)) return;
    const result = await DeleteMachinesApi({ data: { machines, userId: userid.value } });
    if (result?.code === 1) toast.success("删除成功"); else toast.error("删除失败");
    getList();
}

const startEditIp = (row) => {
    editingIpId.value = row.id
    editingIpValue.value = row.robotIp || ''
}

const cancelEditIp = () => {
    editingIpId.value = null
    editingIpValue.value = ''
}

const saveRobotIp = async (row) => {
    const nextIp = editingIpValue.value.trim()
    if (!nextIp) { toast.warning("请输入机器人 IP 地址"); return; }
    const result = await UpdateMachineIpApi({ id: row.id, userId: userid.value, robotIp: nextIp })
    if (result?.code === 1) {
        toast.success("机器人 IP 已更新")
        cancelEditIp()
        getList()
    } else {
        toast.error(result?.msg || "修改 IP 失败")
    }
}

function addmachine() { add.value = true }
function close() {
    add.value = false;
    MachinesInfo = ref({ machines: '', connectionId: '', robotIp: '', userId: userid.value });
}

const tableData = ref([])
</script>

<template>
  <div class="ml-root">

    <!-- 顶栏 -->
    <div class="page-header">
      <div class="page-header-left">
        <div class="page-title-icon">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <rect x="2" y="3" width="12" height="10" rx="2" stroke="white" stroke-width="1.4"/>
            <path d="M5 3V2M11 3V2" stroke="white" stroke-width="1.4" stroke-linecap="round"/>
            <circle cx="8" cy="8" r="2" stroke="white" stroke-width="1.3"/>
          </svg>
        </div>
        <div>
          <div class="page-title">设备列表</div>
          <div class="page-sub">共 {{ tableData.length }} 台设备</div>
        </div>
      </div>
      <button class="btn-add" @click="addmachine">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0">
          <path d="M7 2v10M2 7h10" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
        添加设备
      </button>
    </div>

    <!-- 表格 -->
    <div class="table-wrap" v-if="!haveNot">
      <el-table
        :data="tableData"
        style="width:100%; border-radius:14px; overflow:hidden;"
        :header-cell-style="{ background:'#FFF5F0', color:'#8A4030', fontWeight:'600', fontSize:'13px', padding:'14px 0', borderBottom:'1px solid rgba(255,160,120,0.2)' }"
        :cell-style="{ fontSize:'13px', color:'#3A2010', padding:'14px 0', borderBottom:'1px solid rgba(255,160,120,0.08)' }"
      >
        <el-table-column type="index" label="#" width="60" align="center"/>
        <el-table-column prop="machines" label="设备名称" align="left" min-width="220">
          <template #default="{ row }">
            <div class="device-cell">
              <div class="device-icon">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <rect x="1" y="2" width="12" height="10" rx="1.5" stroke="currentColor" stroke-width="1.3"/>
                  <circle cx="7" cy="7" r="2" stroke="currentColor" stroke-width="1.2"/>
                </svg>
              </div>
              <span class="device-name">{{ row.machines }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="connectionId" label="设备号" align="center" min-width="240">
          <template #default="{ row }">
            <span class="device-id">{{ row.connectionId }}</span>
          </template>
        </el-table-column>
        <el-table-column label="树莓派 IP" align="center" min-width="260">
          <template #default="{ row }">
            <div v-if="editingIpId === row.id" class="ip-edit">
              <input class="ip-input" v-model="editingIpValue" placeholder="例如: 192.168.1.23"/>
              <button class="ip-btn save" @click="saveRobotIp(row)">保存</button>
              <button class="ip-btn cancel" @click="cancelEditIp">取消</button>
            </div>
            <div v-else class="ip-cell">
              <span class="device-ip">{{ row.robotIp || '未配置' }}</span>
              <button class="ip-btn" @click="startEditIp(row)">修改</button>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="110" align="center">
          <template #default="{ row }">
            <button class="op-btn" @click="deleteMachine(row.machines)">
              <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
                <path d="M2 3h7M4 3V2h3v1M3 3l.5 6h4l.5-6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              删除
            </button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-if="haveNot">
      <div class="empty-icon">🤖</div>
      <div class="empty-title">暂无关联设备</div>
      <div class="empty-sub">添加机器人设备后，即可绑定事件并查看健康数据</div>
      <button class="btn-add" style="margin-top:20px; width:auto;" @click="addmachine">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0">
          <path d="M7 2v10M2 7h10" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
        添加设备
      </button>
    </div>

    <!-- 遮罩 -->
    <transition name="mask-fade">
      <div class="modal-mask" v-if="add" @click.self="close"></div>
    </transition>

    <!-- 弹窗 -->
    <transition name="modal-pop">
      <div class="modal" v-if="add">
        <div class="modal-header">
          <div class="modal-title">添加设备</div>
          <button class="modal-close" @click="close">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M4 4l8 8M12 4l-8 8" stroke="#A08070" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <label class="form-label">设备名称</label>
            <input class="form-input" v-model="MachinesInfo.machines" placeholder="请输入设备名称"/>
          </div>
          <div class="form-row">
            <label class="form-label">设备号</label>
            <input class="form-input" v-model="MachinesInfo.connectionId" placeholder="请输入设备号"/>
          </div>
          <div class="form-row">
            <label class="form-label">机器人 IP 地址</label>
            <input class="form-input" v-model="MachinesInfo.robotIp" placeholder="例如: 10.22.231.97"/>
          </div>
          <div class="form-tip">
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none" style="flex-shrink:0;margin-top:1px">
              <circle cx="6.5" cy="6.5" r="5.5" stroke="#E07040" stroke-width="1.2"/>
              <path d="M6.5 6v3.5M6.5 4.5v.5" stroke="#E07040" stroke-width="1.3" stroke-linecap="round"/>
            </svg>
            设备号可在机器人设备标签或管理后台中查看
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn-cancel" @click="close">取消</button>
          <button class="modal-btn-confirm" @click="AddMachine">{{ canadd }}</button>
        </div>
      </div>
    </transition>

  </div>
</template>

<style scoped>
.ml-root {
  width: 100%; height: 100%;
  padding: 20px 24px; box-sizing: border-box;
  display: flex; flex-direction: column; gap: 16px;
  overflow: hidden; position: relative;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

/* 顶栏 */
.page-header { display: flex; align-items: center; justify-content: space-between; flex-shrink: 0; }
.page-header-left { display: flex; align-items: center; gap: 12px; }
.page-title-icon {
  width: 40px; height: 40px; border-radius: 12px;
  background: linear-gradient(135deg, #FF9A76, #FF6040);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(255,96,64,0.28); flex-shrink: 0;
}
.page-title { font-size: 18px; font-weight: 700; color: #3A2010; }
.page-sub { font-size: 12px; color: #B09080; margin-top: 2px; }

/* 添加按钮 */
.btn-add {
  display: flex; align-items: center; gap: 6px;
  width: auto; height: 38px; padding: 0 18px;
  background: linear-gradient(90deg, #FF9A76, #FF6040);
  color: white; border: none; border-radius: 10px;
  font-size: 13px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.2s ease;
  box-shadow: 0 3px 10px rgba(255,96,64,0.28);
}
.btn-add:hover { transform: translateY(-1px); box-shadow: 0 5px 14px rgba(255,96,64,0.36); }

/* 表格 */
.table-wrap {
  flex: 1; overflow-y: auto; border-radius: 14px;
  border: 1px solid rgba(255,160,120,0.15);
  box-shadow: 0 4px 20px rgba(200,90,50,0.06); background: #FFFFFF;
}
.table-wrap::-webkit-scrollbar { width: 4px; }
.table-wrap::-webkit-scrollbar-thumb { background: rgba(255,160,120,0.3); border-radius: 4px; }

.device-cell { display: flex; align-items: center; gap: 10px; padding-left: 4px; }
.device-icon {
  width: 32px; height: 32px; border-radius: 9px; flex-shrink: 0;
  background: linear-gradient(135deg, #FFF0E8, #FFDECA);
  border: 1px solid rgba(255,160,100,0.2);
  display: flex; align-items: center; justify-content: center;
  color: #D86030;
}
.device-name { font-size: 13.5px; font-weight: 600; color: #3A2010; }
.device-id { font-size: 12.5px; color: #7A5040; font-family: monospace; letter-spacing: 0.05em; }
.device-ip { font-size: 12.5px; color: #5F4638; font-family: monospace; }

.ip-cell,
.ip-edit {
  display: flex; align-items: center; justify-content: center; gap: 8px;
}

.ip-input {
  width: 130px; height: 30px;
  border: 1px solid rgba(255,160,120,0.32);
  border-radius: 8px;
  padding: 0 8px;
  font-size: 12px;
  font-family: monospace;
  color: #3A2010;
  background: #FFFAF7;
  outline: none;
}

.ip-btn {
  height: 28px; padding: 0 10px;
  border: 1px solid rgba(255,150,100,0.25);
  border-radius: 8px;
  background: #FFF5F0;
  color: #C85A32;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.ip-btn.save { background: #EAF7F1; color: #16845B; border-color: rgba(22,132,91,0.18); }
.ip-btn.cancel { background: #F5EDE8; color: #8A5040; }

/* 操作按钮 */
.op-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 4px;
  width: 68px; height: 30px; padding: 0;
  border: none; border-radius: 8px;
  font-size: 12px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.18s ease;
  background: #FFF0F0; color: #C03030;
}
.op-btn:hover { background: #FFE0E0; }

/* 空状态 */
.empty-state {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 8px;
  background: #FFFFFF; border-radius: 14px;
  border: 1px solid rgba(255,160,120,0.15);
  box-shadow: 0 4px 20px rgba(200,90,50,0.06);
}
.empty-icon { font-size: 40px; }
.empty-title { font-size: 16px; font-weight: 700; color: #5A3020; }
.empty-sub { font-size: 13px; color: #B09080; }

/* 遮罩 */
.modal-mask {
  position: fixed; inset: 0;
  background: rgba(40,20,10,0.35); backdrop-filter: blur(3px); z-index: 200;
}

/* 弹窗 */
.modal {
  position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
  width: 92%; max-width: 420px;
  background: #FFFFFF; border-radius: 20px;
  box-shadow: 0 24px 64px rgba(100,40,10,0.18);
  z-index: 201; display: flex; flex-direction: column; overflow: hidden;
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 22px 14px;
  border-bottom: 1px solid rgba(255,160,120,0.12);
}
.modal-title { font-size: 16px; font-weight: 700; color: #3A2010; }
.modal-close {
  width: 30px; height: 30px; border-radius: 8px;
  background: #FFF5F0; border: none;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: background 0.18s;
}
.modal-close:hover { background: #FFE8DC; }

.modal-body { padding: 20px 22px; display: flex; flex-direction: column; gap: 14px; }
.form-row { display: flex; flex-direction: column; gap: 5px; }
.form-label { font-size: 12.5px; font-weight: 600; color: #6A4030; }
.form-input {
  width: 100%; height: 40px;
  border: 1px solid rgba(255,160,120,0.3); border-radius: 10px;
  padding: 0 12px; font-size: 13px; font-family: inherit;
  color: #3A2010; background: #FFFAF7; outline: none;
  box-sizing: border-box; transition: border-color 0.2s, background 0.2s;
}
.form-input:focus { border-color: #FF8A65; background: #FFFFFF; }
.form-input::placeholder { color: #C4A898; }

.form-tip {
  display: flex; gap: 7px; align-items: flex-start;
  background: #FFF8F5; border: 1px solid rgba(255,150,100,0.18);
  border-left: 3px solid #FF9A76; border-radius: 0 8px 8px 0;
  padding: 9px 12px; font-size: 12px; color: #8A5040; line-height: 1.6;
}

.modal-footer {
  display: flex; gap: 10px; padding: 14px 22px 18px;
  border-top: 1px solid rgba(255,160,120,0.1);
}
.modal-btn-cancel {
  flex: 1; width: 0; height: 40px;
  background: #F5EDE8; color: #8A5040;
  border: 1px solid rgba(200,130,100,0.2); border-radius: 10px;
  font-size: 14px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.18s;
}
.modal-btn-cancel:hover { background: #FFE4D4; }
.modal-btn-confirm {
  flex: 2; width: 0; height: 40px;
  background: linear-gradient(90deg, #FF9A76, #FF6040);
  color: white; border: none; border-radius: 10px;
  font-size: 14px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.2s ease;
  box-shadow: 0 3px 10px rgba(255,96,64,0.28);
}
.modal-btn-confirm:hover { transform: translateY(-1px); box-shadow: 0 5px 14px rgba(255,96,64,0.36); }

/* 动画 */
.mask-fade-enter-active, .mask-fade-leave-active { transition: opacity 0.25s ease; }
.mask-fade-enter-from, .mask-fade-leave-to { opacity: 0; }
.modal-pop-enter-active { animation: popIn 0.3s cubic-bezier(0.34,1.56,0.64,1); }
.modal-pop-leave-active { animation: popOut 0.2s ease forwards; }
@keyframes popIn {
  from { opacity:0; transform:translate(-50%,-46%) scale(0.92); }
  to   { opacity:1; transform:translate(-50%,-50%) scale(1); }
}
@keyframes popOut { to { opacity:0; transform:translate(-50%,-46%) scale(0.94); } }

@media (max-width: 768px) {
  .ml-root { padding: 12px; gap: 10px; }
  .page-header { flex-wrap: wrap; gap: 10px; }
  .btn-add { width: auto; }
  .modal { width: 96%; max-width: none; }
}
</style>
