<script setup>
    import{ref,onMounted} from 'vue';
    import{GetMachineListApi} from '@/api/users.js';
    import { AddMachineApi } from '../../api/users';
    import { DeleteMachinesApi } from '../../api/users';
    import { useRoute } from 'vue-router';

    const route = useRoute()
    let haveNot = ref(true)
    let add = ref(false)
    let canadd = ref("添加")
    let userid = ref(localStorage.getItem('Id'));
    let MachinesInfo = ref({
        machines: '',
        connectionId:'',
        userId: userid
    })

    onMounted(()=>{
        //userid.value = route.query.userId || '';
        //console.log(userid.value);
        //const userId = localStorage.getItem('Id');
        //userid.value = userId;
        getList();
    })

    //获取设备列表
    const getList = async()=>{
        const userId = userid.value;
        const result = await GetMachineListApi(userId);
        if(result && result.code === 1){
            if(result.data && result.data.rows && result.data.rows.length > 0){
                tableData.value = result.data.rows;
                haveNot.value=false;
                return;
            }
            else{
                tableData.value = [];
                haveNot.value = true;
            }
        }
        else{
            alert("获取表格数据失败")
            return;
        }
    }

    //添加设备
    const AddMachine = async()=>{

        if(!MachinesInfo.value.machines || !MachinesInfo.value.connectionId){
            alert("请输入完整内容");
            close();
            return;
        }

        canadd.value="添加中...";
        const data = MachinesInfo.value
        console.log(data);
        
        
        const result = await AddMachineApi(data);
        if(result && result.code === 1){
            alert("添加事件成功");
            canadd.value="添加";
            getList();
            close();
        }
        else{
            alert("添加事件失败");
            canadd.value="添加";
            getList();
            close();
        }
    }

    const deleteMachine = async(machines)=>{

        if(!confirm(`确定要删除设备 "${machines}" 吗？`)){
            return;
        }

        const result = await DeleteMachinesApi({
            data:{
                machines,
                userId: userid.value
            }
        });
        if(result && result.code === 1){
            alert("删除成功");
            getList();
        }
        else{
            alert("删除失败");
            getList();
        }
    }

    function addmachine(){
        add.value = true;
    }

    function close(){
        add.value = false;
        MachinesInfo = ref({
            machines: '',
            connectionId:'',
            userId: userid
        })
    }

    const tableData = ref([])
</script>

<template>
    <div class="element_container1">
        <div id="title">设备列表</div>
        <div class="table">
            <el-table :data="tableData" border style="width: 1000px" v-if="haveNot==false">
                <el-table-column type="index" label="序号" width="80px" align="center"/>
                <el-table-column prop="machines" label="设备名" width="360px" align="center"/>
                <el-table-column prop="connectionId" label="设备号" width="360px" align="center"/>
                <el-table-column prop="" label="操作" width="200px">
                    <template #default="scoped">
                        <el-button type="danger" size="large" @click="deleteMachine(scoped.row.machines)">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>

        </div>
        <div id="haveNot" v-if="haveNot">
            还没有关联的设备，请添加设备
        </div>
        <button id="addElement" @click="addmachine">添加设备</button>

        <div v-if="add" class="addMachine">
            <p id="addElement_title">添加联系人</p>

            <p class="s">设备名</p>
            <input v-model="MachinesInfo.machines" type="text" class="textInput" placeholder="设备名:">

            <p class="s">设备号</p>
            <input v-model="MachinesInfo.connectionId" type="text" class="textInput" placeholder="设备号:">

            <div id="choice_container">
                <button id="add_button" @click="AddMachine">{{canadd}}</button>
                <button id="add_button" @click="close">取消</button>
            </div>
        </div>
    </div>
</template>

<style>
    /* 全局容器 - 百分比布局 + 无滚动条 */
.element_container1 {
  position: relative;
  width: 100%;
  height: 100vh;
  padding: 1.5%;
  margin: 0;
  box-sizing: border-box;
  background-color: #fdf6f0;
  display: block;
  overflow: hidden;
}

/* 标题 */
#title {
  width: 100%;
  height: 8%;
  font-size: clamp(18px, 3vh, 28px);
  font-weight: 700;
  color: #855ce5;
  text-align: left;
  margin: 0 0 0.5% 0;
  padding-left: 1.5%;
  box-sizing: border-box;
  line-height: 100%;
}

/* 表格区域 —— 从上到下 */
.table {
  width: 100%;
  display: block;
  margin: 0 0 1% 0;
  padding: 0;
}

/* 空数据提示 */
#haveNot {
  width: 97%;
  height: 40vh;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: clamp(16px, 3vh, 24px);
  color: #795548;
  font-weight: 600;
  margin: 0 1.5% 1% 1.5%;
}

/* 添加设备按钮 —— 靠左 */
#addElement {
  width: 8%;
  min-width: 120px;
  height: 5%;
  min-height: 36px;
  background-color: #855ce5;
  color: #fff;
  font-size: clamp(13px, 1.8vh, 15px);
  font-weight: 600;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  display: block;
  margin: 0 0 0 1.5%;
  transition: 0.2s;
}
#addElement:hover {
  background-color: #724bd1;
}

/* ========== 添加设备弹窗 居中 统一风格 ========== */
.addMachine {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 460px;
  height: auto;
  max-height: 70vh;
  background-color: #ffffff;
  border: 1px solid #e5b3a1;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  z-index: 999;
  padding: 3% 2% 3%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-y: auto;
  scrollbar-width: none;
}
.addMachine::-webkit-scrollbar {
  display: none;
}

/* 弹窗标题 */
#addElement_title {
  font-size: clamp(16px, 3vh, 20px);
  font-weight: 600;
  color: #855ce5;
  margin-bottom: 6%;
  text-align: center;
}

/* 输入框标签 */
.s {
  width: 90%;
  font-size: clamp(13px, 2vh, 15px);
  font-weight: 500;
  color: #5d4037;
  margin: 3% 0 1.5%;
  text-align: left;
}

/* 输入框样式（完全统一） */
.textInput {
  width: 90%;
  height: 5vh;
  min-height: 38px;
  border: 1px solid #d1c7c2;
  border-radius: 6px;
  padding: 0 10px;
  font-size: clamp(12px, 1.8vh, 14px);
  background-color: #fffcf9;
  box-sizing: border-box;
  margin-bottom: 3%;
  outline-color: #855ce5;
}

/* 按钮容器 */
#choice_container {
  width: 90%;
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 6%;
}

/* 弹窗按钮（完全沿用你喜欢的样式） */
#add_button {
  width: 100px;
  height: 38px;
  font-size: clamp(12px, 1.8vh, 15px);
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.2s;
}
/* 确定按钮 */
#add_button:first-of-type {
  background-color: #855ce5;
  color: #fff;
}
#add_button:first-of-type:hover {
  background-color: #724bd1;
}
/* 取消按钮 */
#add_button:last-of-type {
  background-color: #d7ccc8;
  color: #333;
}
#add_button:last-of-type:hover {
  background-color: #c8b4ac;
}
</style>