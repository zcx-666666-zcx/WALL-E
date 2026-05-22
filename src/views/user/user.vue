<script setup>
import { ref, onMounted } from 'vue';
import { GetContactsListApi } from '@/api/users.js';
import { AddContractUserApi } from '../../api/users';
import { DeleteContractUserApi } from '../../api/users';
import { toast, confirm } from '../../utils/toast';

let haveNot = ref(true)
let add = ref(false)
let canadd = ref("添加")
let userid = ref(localStorage.getItem('Id'))
let UserInfo = ref({ userId: userid.value, contractName: '', contractPhoneNumber: '' })

onMounted(() => { getList() })

const getList = async () => {
    const result = await GetContactsListApi(userid.value);
    if (result && result.code === 1) {
        if (result.data?.rows?.length > 0) { tableData.value = result.data.rows; haveNot.value = false; }
        else { tableData.value = []; haveNot.value = true; }
    } else { toast.error("获取表格数据失败"); haveNot.value = true; }
    canadd.value = "添加";
}

const AddUser = async () => {
    if (!UserInfo.value.contractName || !UserInfo.value.contractPhoneNumber) { toast.warning("请输入完整信息"); return; }
    canadd.value = "添加中…";
    const result = await AddContractUserApi(UserInfo.value);
    if (result?.code) toast.success("添加联系人成功"); else toast.error("添加联系人失败");
    canadd.value = "添加"; getList(); close();
}

const deleteUser = async (contractName) => {
    if (!await confirm(`确定要删除联系人「${contractName}」吗？`)) return;
    const result = await DeleteContractUserApi({ data: { contractName, userId: userid.value } });
    if (result?.code === 1) toast.success("删除成功"); else toast.error("删除失败");
    getList();
}

function adduser() { add.value = true }
function close() { add.value = false; UserInfo = ref({ userId: userid.value, contractName: '', contractPhoneNumber: '' }); }

const tableData = ref([])
</script>

<template>
  <div class="cl-root">

    <div class="page-header">
      <div class="page-header-left">
        <div class="page-title-icon">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="6" cy="5" r="2.5" stroke="white" stroke-width="1.4"/>
            <path d="M1 13c0-3 2.5-5 5-5s5 2 5 5" stroke="white" stroke-width="1.4" stroke-linecap="round"/>
            <path d="M12 6v4M14 8h-4" stroke="white" stroke-width="1.4" stroke-linecap="round"/>
          </svg>
        </div>
        <div>
          <div class="page-title">联系人列表</div>
          <div class="page-sub">共 {{ tableData.length }} 位联系人</div>
        </div>
      </div>
      <button class="btn-add" @click="adduser">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0">
          <path d="M7 2v10M2 7h10" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
        添加联系人
      </button>
    </div>

    <div class="table-wrap" v-if="!haveNot">
      <el-table
        :data="tableData"
        style="width:100%; border-radius:14px; overflow:hidden;"
        :header-cell-style="{ background:'#FFF5F0', color:'#8A4030', fontWeight:'600', fontSize:'13px', padding:'14px 0', borderBottom:'1px solid rgba(255,160,120,0.2)' }"
        :cell-style="{ fontSize:'13px', color:'#3A2010', padding:'14px 0', borderBottom:'1px solid rgba(255,160,120,0.08)' }"
      >
        <el-table-column type="index" label="#" width="60" align="center"/>
        <el-table-column prop="contractName" label="联系人" align="left" min-width="200">
          <template #default="{ row }">
            <div class="contact-cell">
              <div class="contact-avatar">{{ row.contractName?.[0] ?? '?' }}</div>
              <span class="contact-name">{{ row.contractName }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="contractPhoneNumber" label="手机号码" align="center" min-width="180">
          <template #default="{ row }">
            <span class="phone-text">{{ row.contractPhoneNumber }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <button class="op-btn" @click="deleteUser(row.contractName)">
              <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
                <path d="M2 3h7M4 3V2h3v1M3 3l.5 6h4l.5-6" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              删除
            </button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="empty-state" v-if="haveNot">
      <div class="empty-icon">👥</div>
      <div class="empty-title">暂无联系人</div>
      <div class="empty-sub">添加紧急联系人，异常时可第一时间通知家属</div>
      <button class="btn-add" style="margin-top:20px" @click="adduser">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0">
          <path d="M7 2v10M2 7h10" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
        添加联系人
      </button>
    </div>

    <transition name="mask-fade">
      <div class="modal-mask" v-if="add" @click.self="close"></div>
    </transition>

    <transition name="modal-pop">
      <div class="modal" v-if="add">
        <div class="modal-header">
          <div class="modal-title">添加联系人</div>
          <button class="modal-close" @click="close">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M4 4l8 8M12 4l-8 8" stroke="#A08070" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <label class="form-label">联系人姓名</label>
            <input class="form-input" v-model="UserInfo.contractName" placeholder="请输入姓名"/>
          </div>
          <div class="form-row">
            <label class="form-label">手机号码</label>
            <input class="form-input" v-model="UserInfo.contractPhoneNumber" type="tel" placeholder="请输入手机号码"/>
          </div>
        </div>
        <div class="modal-footer">
          <button class="modal-btn-cancel" @click="close">取消</button>
          <button class="modal-btn-confirm" @click="AddUser">{{ canadd }}</button>
        </div>
      </div>
    </transition>

  </div>
</template>

<style scoped>
.btn-add{
    width: 8%;
}
.cl-root {
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
.page-title { font-size: 18px; font-weight: 700; color: #3A2010; }
.page-sub { font-size: 12px; color: #B09080; margin-top: 2px; }
.btn-add {
  display: flex; align-items: center; gap: 6px;
  height: 38px; padding: 0 18px;
  background: linear-gradient(90deg, #FF9A76, #FF6040);
  color: white; border: none; border-radius: 10px;
  font-size: 13px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.2s ease;
  box-shadow: 0 3px 10px rgba(255,96,64,0.28);
}
.btn-add:hover { transform: translateY(-1px); box-shadow: 0 5px 14px rgba(255,96,64,0.36); }

.table-wrap {
  flex: 1; overflow-y: auto; border-radius: 14px;
  border: 1px solid rgba(255,160,120,0.15);
  box-shadow: 0 4px 20px rgba(200,90,50,0.06); background: #FFFFFF;
}
.table-wrap::-webkit-scrollbar { width: 4px; }
.table-wrap::-webkit-scrollbar-thumb { background: rgba(255,160,120,0.3); border-radius: 4px; }

.contact-cell { display: flex; align-items: center; gap: 10px; padding-left: 4px; }
.contact-avatar {
  width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, #FFB899, #FF8A65);
  color: white; font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 6px rgba(255,112,67,0.2);
}
.contact-name { font-size: 13.5px; font-weight: 600; color: #3A2010; }
.phone-text { font-size: 13px; color: #7A5040; font-family: monospace; letter-spacing: 0.04em; }

.op-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 4px;
  height: 30px; padding: 0 12px; border: none; border-radius: 8px; width: 80%;
  font-size: 12px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.18s ease;
  background: #FFF0F0; color: #C03030;
}
.op-btn:hover { background: #FFE0E0; }

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

.modal-mask {
  position: fixed; inset: 0;
  background: rgba(40,20,10,0.35); backdrop-filter: blur(3px); z-index: 200;
}
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
  width: 30px; height: 30px; border-radius: 8px; background: #FFF5F0; border: none;
  display: flex; align-items: center; justify-content: center; cursor: pointer; transition: background 0.18s;
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
.modal-footer {
  display: flex; gap: 10px; padding: 14px 22px 18px;
  border-top: 1px solid rgba(255,160,120,0.1);
}
.modal-btn-cancel {
  flex: 1; height: 40px; background: #F5EDE8; color: #8A5040;
  border: 1px solid rgba(200,130,100,0.2); border-radius: 10px;
  font-size: 14px; font-weight: 600; font-family: inherit; cursor: pointer; transition: all 0.18s;
}
.modal-btn-cancel:hover { background: #FFE4D4; }
.modal-btn-confirm {
  flex: 2; height: 40px;
  background: linear-gradient(90deg, #FF9A76, #FF6040);
  color: white; border: none; border-radius: 10px;
  font-size: 14px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.2s ease;
  box-shadow: 0 3px 10px rgba(255,96,64,0.28);
}
.modal-btn-confirm:hover { transform: translateY(-1px); box-shadow: 0 5px 14px rgba(255,96,64,0.36); }

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
  .cl-root { padding: 12px; gap: 10px; }
  .page-header { flex-wrap: wrap; gap: 10px; }
  .btn-add { width: auto; }
  .modal { width: 96%; max-width: none; }
}
</style>