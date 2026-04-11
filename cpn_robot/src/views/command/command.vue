<script setup>
    import{ref,onMounted,watch} from 'vue';
    import { GetCommandListApi } from '../../api/users';
    import { useRoute } from 'vue-router';

    let haveNot = ref(false)
    const route = useRoute()
    let machine_name = ref('');
    let userid = ref(localStorage.getItem('Id'))

    onMounted(()=>{
        machine_name.value = route.query.machineName || '';
        getCommandList();
    })

    //获取命令列表
    const getCommandList = async()=>{
        const machines = machine_name.value;
        const userId = userid.value;
        console.log(machines,userId);
        const data ={machines,userId}
        
        const result = await GetCommandListApi(data);
        if(result && result.code === 1){
            if(result.data && result.data.rows && result.data.rows.length > 0){
                tableData.value = result.data.rows;
                return;
            }
            console.log("行",machine_name.value);
            
            tableData.value = []
        }
        else{
            alert("获取表格数据失败")
            tableData.value = []
        }
    }

    watch(() => route.query.machineName, (newValue) => {
        console.log('machine_name changed to:', newValue);
        machine_name.value = newValue || '';
        getCommandList();
    }, { immediate: true });

    const tableData = ref([
        
    ])
</script>

<template>
    <div class="command_container1">
    <div id="title">命令列表</div>
    <div class="table">
        <el-table :data="tableData" border style="width: 880px" v-if="haveNot==false">
            <el-table-column type="index" label="序号" width="80px" align="center"/>
            <el-table-column prop="commandName" label="命令名" width="250px" align="center"/>
            <el-table-column prop="commandCode" label="执行状态" width="250px" align="center"/>
            <el-table-column prop="time" label="执行时间" width="300px" align="center"/>
        </el-table>
    </div>
    <div id="haveNot" v-if="haveNot">
        暂无执行的命令
    </div>
</div>
</template>

<style>
    .command_container1{
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
</style>