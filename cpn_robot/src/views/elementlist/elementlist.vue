<script setup>
    import{ref,onMounted} from 'vue';
    import{GetElementListApi} from '@/api/users.js';
    import { AddElementApi } from '../../api/users';
    import { DeleteElementApi } from '../../api/users';
    import { EditElementApi } from '../../api/users';
    import { UpdateElementApi } from '../../api/users';
    import { useRoute } from 'vue-router'; 

    const route = useRoute()
    let haveNot = ref(true)
    let add = ref(false)
    let canadd = ref("添加")
    let userid = ref(localStorage.getItem('Id'))
    let element = ref({
        eventName:'',
        eventDate:'',
        repeatDays:'11',
        eventTime:'',
        priority:'3',
        description:'',
        machines:'',
        userId: userid.value
    })

    onMounted(()=>{
        //userid.value = route.query.userId || '';
        //console.log(userid.value);
        //const userId = localStorage.getItem('Id');
        console.log(userid.value)
        //userid.value = userId;
        getList();
    })

    //获取列表
    const getList = async()=>{
        const userId = userid.value;
        const result = await GetElementListApi(userId);
        if(result && result.code === 1){
            if(result.data && result.data.rows && result.data.rows.length > 0){
                tableData.value = result.data.rows;
                haveNot.value=false;
                return;
            }
            tableData.value = [];
            haveNot.value = true;
            return;
        }
        else{
            tableData.value = [];
            alert("获取表格数据失败")
            return;
        }
    }

    function OpenAdd(){
        add.value=true
    }

    function close(){
        add.value=false;
        element=ref({
            eventName:'',
            eventDate:'',
            repeatDays:'11',
            eventTime:'',
            priority:'3',
            description:'',
            machines:'',
            userId: userid.value
        });
        canadd.value="添加";
        
    }

    //添加事件
    const AddElement = async()=>{

        console.log(element.value);

        const Element = element.value;

        if(canadd.value === "更新"){
            canadd.value = "更新中"
            updateElement(Element);
            return;
        }   

        canadd.value="添加中...";
        const result = await AddElementApi(Element);
        if(result){
            if(result.code === 1){
                alert("添加事件成功");
                canadd.value="添加";
                getList();
                add = ref(false);
                close();
                return;
            }
            else{
                alert("添加事件失败");
                canadd.value="添加";
                add = ref(false);
                close();
                return;
            }
        }
        alert("添加事件失败");
        canadd.value="添加";
        add = ref(false);
        close();
        return;
    }

    //删除事件
    const deleteElement = async(eventName)=>{
        
        if(!confirm(`确定要删除事件 "${eventName}" 吗？`)){
            return;
        }

        const userId = userid.value;
        console.log(eventName,userId);
        

        const result = await DeleteElementApi({
            data:{
                eventName,
                userId
            }
        });
        if(result && result.code === 1){
            alert("删除成功");
        }
        else{
            alert("删除失败");
        }
        getList();

    }

    //获取单个事件
    const editElement = async(eventName)=>{
        const data = {eventName,userId: userid.value}
        const result = await EditElementApi(data);
        if(result && result.code === 1){
            element=ref({
                eventName: result.data.eventName,
                eventDate: result.data.eventDate,
                repeatDays: result.data.repeatDays,
                eventTime: result.data.eventTime,
                priority: result.data.priority,
                description: result.data.description,
                machines: result.data.machines,
                userId: userid.value
            })
            canadd.value = "更新"
            add.value = true
            console.log(canadd);
            
        }
        else{
            alert("调取异常");
        }
    }

    //更新事件
    const updateElement = async(Element)=>{
        const result = await UpdateElementApi(Element);
        if(result && result.code === 1){
            alert("更新成功");
            getList();
            canadd.value="添加";
            close();
        }
        else{
            alert("更新失败");
        }
    }



    


    const tableData = ref([])
</script>

<template>
    <div class="element_container1">
        <div id="title">事件列表</div>
        <div class="table">
            <el-table :data="tableData" border style="width: 2030px" v-if="haveNot==false">
                <el-table-column type="index" label="序号" width="80px" align="center"/>
                <el-table-column prop="eventName" label="事件名称" width="250px" align="center"/>
                <el-table-column prop="machines" label="绑定对象" width="200px" align="center"/>
                <el-table-column prop="eventDate" label="首次提醒日期" width="250px" align="center"/>
                <el-table-column prop="repeatDays" label="重复提醒" width="150px" align="center"/>
                <el-table-column prop="eventTime" label="提醒时间" width="250px" align="center"/>
                <el-table-column prop="priority" label="优先级" width="100px" align="center"/>
                <el-table-column prop="description" label="事件描述" width="500px" align="center"/>
                <el-table-column prop="" label="操作" width="250px">
                    <template #default="scoped">
                        <el-button type="primary" size="small" @click="editElement(scoped.row.eventName)">编辑</el-button>
                        <el-button type="danger" size="small" @click="deleteElement(scoped.row.eventName)">删除</el-button>
                    </template>
                </el-table-column>
            </el-table>

        </div>
        <div id="haveNot" v-if="haveNot">
            还没有创建事件，请添加事件
        </div>
        <button id="addElement" @click="OpenAdd">添加事件</button>

        <div v-if="add" class="addElement_container">
            <p id="addElement_title">添加事件</p>

            <p class="s">事件名称</p>
            <input v-model="element.eventName" type="text" class="textinput" placeholder="事件名称:">

            <p class="s">首次提醒日期</p>
            <input type="date" class="time" v-model="element.eventDate">

            <p class="s">提醒时间</p>
            <input type="time" class="time" v-model="element.eventTime">

            <p class="s">重复提醒</p>
            <select name="reap" class="select" v-model="element.repeatDays">
                <option value="1">每1天提醒</option>
                <option value="2" >每2天提醒</option>
                <option value="3" >每3天提醒</option>
                <option value="4" >每4天提醒</option>
                <option value="5" >每5天提醒</option>
                <option value="6" >每6天提醒</option>
                <option value="7" >工作日提醒</option>
                <option value="8" >周末提醒</option>
                <option value="9" >每周提醒</option>
                <option value="10" >每月提醒</option>
                <option value="11" >不重复</option>
            </select>

            <p class="s">事件优先级</p>
            <p class="S">若两事件同时提醒，将按照优先级顺序提醒</p>
            <select name="pri" class="select" v-model="element.priority">
                <option value="">事件提示优先级</option>
                <option value="1" >低</option>
                <option value="2" >中</option>
                <option value="3" >高</option>
            </select>

            <p class="s">事件描述</p>
            <p class="S">实际语音提示的内容</p>
            <textarea v-model="element.description" type="textarea" class="textareaInput" placeholder="事件描述:" cols="30" rows="3"></textarea>

            <p class="s">绑定设备</p>
            <input v-model="element.machines" type="text" class="textinput" placeholder="设备号:">
            <div id="choice_container">
                <button id="add_button" @click="AddElement">{{canadd}}</button>
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
    .s{
        font-size: 15px;
        position: relative;
        margin: 0 0 0 0;
        color: rgb(85, 85, 85);
    }
    .S{
        font-size: 8px;
        position: relative;
        margin: 0 0 0 0;
        color: rgb(85, 85, 85);
    }
    .addElement_container{
        position: absolute;
        height: 700px;
        width: 550px;
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
        padding-top: 35px;
    }
    .time{
        margin: 0 0 2px 0;
    }
    .select{
        margin: 0 0 2px 0;
        font-size: 10px;
        width: 110px;
        height: 25px;
    }
    .textinput{
        margin: 0 0 2px 0;

    }
    .textareaInput{
        margin: 0 0 2px 0;
        font-size: 10px;

    }
    #addElement_title{
        color: white;
        position: absolute;
        top: 7px;
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
</style>