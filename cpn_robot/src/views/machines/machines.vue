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
            <el-table :data="tableData" border style="width: 730px" v-if="haveNot==false">
                <el-table-column type="index" label="序号" width="80px" align="center"/>
                <el-table-column prop="machines" label="设备名" width="250px" align="center"/>
                <el-table-column prop="connectionId" label="设备号" width="250px" align="center"/>
                <el-table-column prop="" label="操作" width="150px">
                    <template #default="scoped">
                        <el-button type="danger" size="small" @click="deleteMachine(scoped.row.machines)">删除</el-button>
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
    .element_container1{
        position: relative;
        justify-content: center;
        align-items: center;
    }
    #title{
        height: 40px;
        width: 2000px;
        justify-content: left;
        align-items: center;
        text-align: center;
        display: flex;
        padding: 0 0 0 15px;
        font-size: 27px;
        color: rgb(118, 83, 141);
        font-weight: 800;
        margin: 0 0 20px 0;

    }
    #haveNot{
        margin: 20px 0 0 0;
        height: 280px;
        width: 1960px;
        background-color: white;
        border-radius: 10px;
        position: relative;
        justify-content: center;
        align-items: center;
        text-align: center;
        display: flex;
        font-size: 35px;
        color: rgb(112, 112, 112);
        font-weight: 800;
    }
    #addElement{
        height: 30px;
        width: 100px;
        justify-content: center;
        align-items: center;
        text-align: center;
        display: flex;
        font-size: 16px;
        color: rgb(0, 132, 255);
        font-weight: 800;
        background-color: rgb(194, 194, 194);
        border-radius: 5px;
    }
    .addMachine{
        position: absolute;
        height: 550px;
        width: 400px;
        background-color: rgb(255, 200, 155);
        top: 100px;
        left: 825px;
        opacity: 1;
        z-index: 3;
        border: 2px solid rgb(165, 121, 64);
        border-radius: 7px;
        justify-content: center;
        align-items: center;
        text-align: center;
        flex-direction: column;
        display: flex;
        padding: 10px;
    }
    .textInput{
        margin: 0 0 50px 0;
        height: 35px;
        width: 190px;
    }
</style>