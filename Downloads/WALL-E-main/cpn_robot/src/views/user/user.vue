<script setup>
    import{ref,onMounted} from 'vue';
    import{GetContactsListApi} from '@/api/users.js';
    import { AddContractUserApi } from '../../api/users';
    import { DeleteContractUserApi } from '../../api/users';
    import { useRoute } from 'vue-router';

    const route = useRoute()
    let haveNot = ref(true)
    let add = ref(false)
    let canadd = ref("添加")
    let userid = ref(localStorage.getItem('Id'))

    let UserInfo = ref({
        userId: userid.value,
        contractName:'',
        contractPhoneNumber:''
    })

    onMounted(()=>{
        //userid.value = route.query.userId || '';
        //console.log(userid.value);
        //const userId = localStorage.getItem('Id');
        //userid.value = userId;
        
        getList();
    })

    //获取联系人表
    const getList = async()=>{
        const userId = userid.value
        const result = await GetContactsListApi(userId);
        if(result && result.code === 1){
            if(result.data && result.data.rows && result.data.rows.length > 0){
                tableData.value = result.data.rows;
                haveNot.value=false;
                canadd.value="添加";
                return;
            }
            else{
                tableData.value = [];
                haveNot = ref(true);
                return;
            }
        }
        else{
            alert("获取表格数据失败");
            canadd.value="添加";
            haveNot = ref(true);
            return;
        }
    }

    //添加联系人
    const AddUser = async()=>{
        console.log(UserInfo.value);
        
        if(!UserInfo.value.contractName || !UserInfo.value.contractPhoneNumber){
            alert("请输入完整信息");
            canadd.value="添加";
            close();
            return;
        }
        
        canadd.value="添加中...";
        const result = await AddContractUserApi(UserInfo.value);
        if(result.code){
            alert("添加联系人成功");
            canadd.value="添加";
            getList();
            close();
        }
        else{
            alert("添加联系人失败");
            canadd.value="添加";
            getList();
            close();
        }
    }

    //删除联系人
    const deleteUser = async(contractName)=>{

        if(!confirm(`确定要删除事件 "${contractName}" 吗？`)){
            return;
        }
        const userId = userid.value;
        const result = await DeleteContractUserApi({
            data:{
                contractName,
                userId
            }
        });
        if(result && result.code === 1){
            alert("删除成功");
            getList();
        }
        else{
            alert("删除失败")
            getList();
        }
    }

    function adduser(){
        add.value = true
    }

    function close(){
        add.value = false;
        UserInfo = ref({
            userId: userid.value,
            contractName: '',
            contractPhoneNumber: ''
        })
        
    }

    const tableData = ref([])

</script>

<template>
    <div class="element_container1">
        <div id="title">联系人列表</div>
        <div class="table">
            <el-table :data="tableData" border style="width: 730" v-if="haveNot==false">
                <el-table-column type="index" label="序号" width="80px" align="center"/>
                <el-table-column prop="contractName" label="联系人" width="250px" align="center"/>
                <el-table-column prop="contractPhoneNumber" label="手机号" width="250px" align="center"/>
                <el-table-column prop="" label="操作" width="150px">
                    <template #default="scoped">
                        <el-button type="danger" size="small" @click="deleteUser(scoped.row.contractName)">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>

        </div>
        <div id="haveNot" v-if="haveNot">
            还没有联系人，请添加联系人
        </div>
        <button id="addElement" @click="adduser">添加联系人</button>

        <div v-if="add" class="addUser">
            <p id="addElement_title">添加联系人</p>

            <p class="s">联系人姓名</p>
            <input v-model="UserInfo.contractName" type="text" class="textInput" placeholder="联系人姓名:">

            <p class="s">联系人电话号码</p>
            <input v-model="UserInfo.contractPhoneNumber" type="text" class="textInput" placeholder="电话号码:">

            <div id="choice_container">
                <button id="add_button" @click="AddUser">{{canadd}}</button>
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
        width: 2160px;
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
    .addUser{
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