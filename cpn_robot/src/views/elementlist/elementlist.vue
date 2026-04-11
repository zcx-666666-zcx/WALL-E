<script setup>
    import { ref, onMounted } from 'vue';
    import { GetElementListApi } from '@/api/users.js';
    import { AddElementApi } from '../../api/users';
    import { DeleteElementApi } from '../../api/users';
    import { EditElementApi } from '../../api/users';
    import { UpdateElementApi } from '../../api/users';

    let haveNot = ref(true)
    let add = ref(false)
    let canadd = ref("添加")
    let userid = ref(localStorage.getItem('Id'))
    let element = ref({
        eventName: '',
        eventDate: '',
        repeatDays: '11',
        eventTime: '',
        priority: '3',
        description: '',
        machines: '',
        userId: userid.value
    })

    onMounted(() => {
        console.log(userid.value)
        getList();
    })

    const getList = async () => {
        const userId = userid.value;
        const result = await GetElementListApi(userId);
        if (result && result.code === 1) {
            if (result.data && result.data.rows && result.data.rows.length > 0) {
                tableData.value = result.data.rows;
                haveNot.value = false;
                return;
            }
            tableData.value = [];
            haveNot.value = true;
            return;
        } else {
            tableData.value = [];
            alert("获取表格数据失败");
        }
    }

    function OpenAdd() { add.value = true; }

    function close() {
        add.value = false;
        element = ref({
            eventName: '', eventDate: '', repeatDays: '11',
            eventTime: '', priority: '3', description: '',
            machines: '', userId: userid.value
        });
        canadd.value = "添加";
    }

    const AddElement = async () => {
        const Element = element.value;
        if (canadd.value === "更新") {
            canadd.value = "更新中…";
            updateElement(Element);
            return;
        }
        canadd.value = "添加中…";
        const result = await AddElementApi(Element);
        if (result && result.code === 1) {
            alert("添加事件成功");
            getList();
        } else {
            alert("添加事件失败");
        }
        canadd.value = "添加";
        close();
    }

    const deleteElement = async (eventName) => {
        if (!confirm(`确定要删除事件「${eventName}」吗？`)) return;
        const result = await DeleteElementApi({ data: { eventName, userId: userid.value } });
        alert(result && result.code === 1 ? "删除成功" : "删除失败");
        getList();
    }

    const editElement = async (eventName) => {
        const result = await EditElementApi({ eventName, userId: userid.value });
        if (result && result.code === 1) {
            element = ref({ ...result.data, userId: userid.value });
            canadd.value = "更新";
            add.value = true;
        } else {
            alert("调取异常");
        }
    }

    const updateElement = async (Element) => {
        const result = await UpdateElementApi(Element);
        if (result && result.code === 1) {
            alert("更新成功");
            getList();
            canadd.value = "添加";
            close();
        } else {
            alert("更新失败");
        }
    }

    const priorityLabel = (val) => ({ '1': '低', '2': '中', '3': '高' }[val] || val)
    const priorityClass = (val) => ({ '1': 'pri-low', '2': 'pri-mid', '3': 'pri-high' }[val] || '')

    const tableData = ref([])
</script>

<template>
  <div class="el-root">

    <!-- 顶栏 -->
    <div class="page-header">
      <div class="page-header-left">
        <div class="page-title-icon">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <rect x="2" y="1" width="12" height="14" rx="2" stroke="white" stroke-width="1.4"/>
            <path d="M5 5h6M5 8h6M5 11h4" stroke="white" stroke-width="1.3" stroke-linecap="round"/>
          </svg>
        </div>
        <div>
          <div class="page-title">事件列表</div>
          <div class="page-sub">共 {{ tableData.length }} 条事件</div>
        </div>
      </div>
      <button class="btn-add" @click="OpenAdd">
        <svg width="17" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0">
          <path d="M7 2v10M2 7h10" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
        添加事件
      </button>
    </div>

    <!-- 表格 -->
    <div class="table-wrap" v-if="!haveNot">
      <el-table
        :data="tableData"
        style="width:100%; border-radius:14px; overflow:hidden;"
        :header-cell-style="{
          background: '#FFF5F0',
          color: '#8A4030',
          fontWeight: '600',
          fontSize: '13px',
          padding: '14px 0',
          borderBottom: '1px solid rgba(255,160,120,0.2)'
        }"
        :cell-style="{
          fontSize: '13px',
          color: '#3A2010',
          padding: '13px 0',
          borderBottom: '1px solid rgba(255,160,120,0.08)'
        }"
        :row-style="{ background: '#FFFFFF' }"
      >
        <el-table-column type="index" label="#" width="52" align="center"/>
        <el-table-column prop="eventName" label="事件名称" min-width="180" align="left">
          <template #default="{ row }">
            <span class="event-name">{{ row.eventName }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="machines" label="绑定设备" width="130" align="center"/>
        <el-table-column prop="eventDate" label="首次提醒" width="130" align="center"/>
        <el-table-column prop="repeatDays" label="重复" width="100" align="center">
          <template #default="{ row }">
            <span class="repeat-badge">{{ row.repeatDays === '11' ? '不重复' : '每' + row.repeatDays + '天' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="eventTime" label="时间" width="100" align="center"/>
        <el-table-column prop="priority" label="优先级" width="100" align="center">
          <template #default="{ row }">
            <span class="pri-badge" :class="priorityClass(row.priority)">
              {{ priorityLabel(row.priority) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="事件描述" min-width="200" align="left">
          <template #default="{ row }">
            <span class="desc-text">{{ row.description }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <button class="op-btn op-edit" @click="editElement(row.eventName)">编辑</button>
            <button class="op-btn op-del" @click="deleteElement(row.eventName)">删除</button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-if="haveNot">
      <div class="empty-icon">📋</div>
      <div class="empty-title">暂无事件</div>
      <div class="empty-sub">点击右上角「添加事件」开始创建第一条提醒</div>
      <button class="btn-add" style="margin-top:20px" @click="OpenAdd">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" style="flex-shrink:0">
          <path d="M7 2v10M2 7h10" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
        </svg>
        添加事件
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
          <div class="modal-title">{{ canadd === '更新' || canadd === '更新中…' ? '编辑事件' : '添加事件' }}</div>
          <button class="modal-close" @click="close">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M4 4l8 8M12 4l-8 8" stroke="#A08070" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <div class="form-row">
            <label class="form-label">事件名称</label>
            <input class="form-input" v-model="element.eventName" placeholder="请输入事件名称" />
          </div>

          <div class="form-row-2col">
            <div class="form-row">
              <label class="form-label">首次提醒日期</label>
              <input class="form-input" type="date" v-model="element.eventDate" />
            </div>
            <div class="form-row">
              <label class="form-label">提醒时间</label>
              <input class="form-input" type="time" v-model="element.eventTime" />
            </div>
          </div>

          <div class="form-row-2col">
            <div class="form-row">
              <label class="form-label">重复提醒</label>
              <select class="form-select" v-model="element.repeatDays">
                <option value="1">每 1 天提醒</option>
                <option value="2">每 2 天提醒</option>
                <option value="3">每 3 天提醒</option>
                <option value="4">每 4 天提醒</option>
                <option value="5">每 5 天提醒</option>
                <option value="6">每 6 天提醒</option>
                <option value="7">每 7 天提醒</option>
                <option value="8">每 8 天提醒</option>
                <option value="9">每 9 天提醒</option>
                <option value="10">每 10 天提醒</option>
                <option value="11">不重复</option>
              </select>
            </div>
            <div class="form-row">
              <label class="form-label">
                事件优先级
                <span class="label-hint">同时提醒时按优先级排序</span>
              </label>
              <select class="form-select" v-model="element.priority">
                <option value="1">低</option>
                <option value="2">中</option>
                <option value="3">高</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <label class="form-label">
              事件描述
              <span class="label-hint">实际语音播报的内容</span>
            </label>
            <textarea class="form-textarea" v-model="element.description" placeholder="请输入事件描述…"></textarea>
          </div>

          <div class="form-row">
            <label class="form-label">绑定设备</label>
            <input class="form-input" v-model="element.machines" placeholder="请输入设备号" />
          </div>
        </div>

        <div class="modal-footer">
          <button class="modal-btn-cancel" @click="close">取消</button>
          <button class="modal-btn-confirm" @click="AddElement">{{ canadd }}</button>
        </div>
      </div>
    </transition>

  </div>
</template>

<style scoped>
/* ══ 根容器 ══ */
.el-root {
  width: 100%;
  height: 100%;
  padding: 20px 24px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow: hidden;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  position: relative;
}

/* ══ 顶栏 ══ */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}
.page-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.page-title-icon {
  width: 40px; height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #FF9A76, #FF6040);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(255,96,64,0.28);
  flex-shrink: 0;
}
.page-title {
  font-size: 18px;
  font-weight: 700;
  color: #3A2010;
  letter-spacing: 0.01em;
}
.page-sub {
  font-size: 12px;
  color: #B09080;
  margin-top: 2px;
}

.btn-add {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 10%;
  height: 38px;
  padding: 0 18px;
  background: linear-gradient(90deg, #FF9A76, #FF6040);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 3px 10px rgba(255,96,64,0.28);
}
.btn-add:hover {
  transform: translateY(-1px);
  box-shadow: 0 5px 14px rgba(255,96,64,0.36);
}

/* ══ 表格 ══ */
.table-wrap {
  flex: 1;
  overflow-y: auto;
  border-radius: 14px;
  border: 1px solid rgba(255,160,120,0.15);
  box-shadow: 0 4px 20px rgba(200,90,50,0.06);
  background: #FFFFFF;
}
.table-wrap::-webkit-scrollbar { width: 4px; }
.table-wrap::-webkit-scrollbar-thumb { background: rgba(255,160,120,0.3); border-radius: 4px; }

.event-name {
  font-weight: 600;
  color: #3A2010;
}
.desc-text {
  color: #7A5040;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.repeat-badge {
  font-size: 11px;
  background: #FFF0E8;
  color: #C06030;
  border-radius: 100px;
  padding: 2px 8px;
  border: 1px solid rgba(255,140,80,0.2);
}
.pri-badge {
  font-size: 11px;
  font-weight: 600;
  border-radius: 100px;
  padding: 3px 10px;
  border: 1px solid transparent;
}
.pri-low  { background: #F0F7EE; color: #4A7A40; border-color: rgba(80,160,60,0.2); }
.pri-mid  { background: #FFF8E8; color: #A06020; border-color: rgba(200,140,40,0.2); }
.pri-high { background: #FFF0EE; color: #C03030; border-color: rgba(200,60,40,0.2); }

.op-btn {
  height: 30px;
  width: 28%;
  padding: 0 10px;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.18s ease;
}
.op-edit {
  background: #FFF0E8;
  color: #D06030;
  margin-right: 6px;
}
.op-edit:hover { background: #FFE4D4; }
.op-del {
  background: #FFF0F0;
  color: #C03030;
}
.op-del:hover { background: #FFE0E0; }

/* ══ 空状态 ══ */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: #FFFFFF;
  border-radius: 14px;
  border: 1px solid rgba(255,160,120,0.15);
  box-shadow: 0 4px 20px rgba(200,90,50,0.06);
}
.empty-icon { font-size: 40px; }
.empty-title { font-size: 16px; font-weight: 700; color: #5A3020; }
.empty-sub { font-size: 13px; color: #B09080; }

/* ══ 遮罩 ══ */
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(40, 20, 10, 0.35);
  backdrop-filter: blur(3px);
  z-index: 200;
}

/* ══ 弹窗 ══ */
.modal {
  position: fixed;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 92%;
  max-width: 540px;
  max-height: 88vh;
  background: #FFFFFF;
  border-radius: 20px;
  box-shadow: 0 24px 64px rgba(100, 40, 10, 0.18);
  z-index: 201;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 22px 14px;
  border-bottom: 1px solid rgba(255,160,120,0.12);
  flex-shrink: 0;
}
.modal-title {
  font-size: 16px;
  font-weight: 700;
  color: #3A2010;
  letter-spacing: 0.01em;
}
.modal-close {
  width: 30px; height: 30px;
  border-radius: 8px;
  background: #FFF5F0;
  border: none;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: background 0.18s;
}
.modal-close:hover { background: #FFE8DC; }

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 22px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.modal-body::-webkit-scrollbar { width: 4px; }
.modal-body::-webkit-scrollbar-thumb { background: rgba(255,160,120,0.3); border-radius: 4px; }

.form-row {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.form-row-2col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.form-label {
  font-size: 12.5px;
  font-weight: 600;
  color: #6A4030;
  display: flex;
  align-items: center;
  gap: 6px;
}
.label-hint {
  font-weight: 400;
  font-size: 11px;
  color: #B09080;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  height: 38px;
  border: 1px solid rgba(255,160,120,0.3);
  border-radius: 10px;
  padding: 0 12px;
  font-size: 13px;
  font-family: inherit;
  color: #3A2010;
  background: #FFFAF7;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s, background 0.2s;
}
.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  border-color: #FF8A65;
  background: #FFFFFF;
}
.form-input::placeholder,
.form-textarea::placeholder { color: #C4A898; }

.form-textarea {
  height: 80px;
  resize: none;
  padding: 10px 12px;
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  gap: 10px;
  padding: 14px 22px 18px;
  border-top: 1px solid rgba(255,160,120,0.1);
  flex-shrink: 0;
}
.modal-btn-cancel {
  flex: 1; height: 40px;
  background: #F5EDE8;
  color: #8A5040;
  border: 1px solid rgba(200,130,100,0.2);
  border-radius: 10px;
  font-size: 14px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.18s;
}
.modal-btn-cancel:hover { background: #FFE4D4; }
.modal-btn-confirm {
  flex: 2; height: 40px;
  background: linear-gradient(90deg, #FF9A76, #FF6040);
  color: white;
  border: none; border-radius: 10px;
  font-size: 14px; font-weight: 600; font-family: inherit;
  cursor: pointer; transition: all 0.2s ease;
  box-shadow: 0 3px 10px rgba(255,96,64,0.28);
}
.modal-btn-confirm:hover {
  transform: translateY(-1px);
  box-shadow: 0 5px 14px rgba(255,96,64,0.36);
}

/* ══ 过渡动画 ══ */
.mask-fade-enter-active, .mask-fade-leave-active { transition: opacity 0.25s ease; }
.mask-fade-enter-from, .mask-fade-leave-to { opacity: 0; }

.modal-pop-enter-active { animation: popIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); }
.modal-pop-leave-active { animation: popOut 0.2s ease forwards; }
@keyframes popIn {
  from { opacity: 0; transform: translate(-50%, -46%) scale(0.92); }
  to   { opacity: 1; transform: translate(-50%, -50%) scale(1); }
}
@keyframes popOut {
  to { opacity: 0; transform: translate(-50%, -46%) scale(0.94); }
}
</style>