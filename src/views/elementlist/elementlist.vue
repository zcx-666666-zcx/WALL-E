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
            <el-table :data="tableData" border style="width: 1600px" v-if="haveNot==false">
                <el-table-column type="index" label="序号" width="60px" align="center"/>
                <el-table-column prop="eventName" label="事件名称" width="200px" align="center"/>
                <el-table-column prop="machines" label="绑定对象" width="120px" align="center"/>
                <el-table-column prop="eventDate" label="首次提醒日期" width="120px" align="center"/>
                <el-table-column prop="repeatDays" label="重复提醒" width="100px" align="center"/>
                <el-table-column prop="eventTime" label="提醒时间" width="120px" align="center"/>
                <el-table-column prop="priority" label="优先级" width="80px" align="center"/>
                <el-table-column prop="description" label="事件描述" width="550px" align="center"/>
                <el-table-column prop="" label="操作" width="250px">
                    <template #default="scoped">
                        <el-button class="BTN" type="primary" size="large" @click="editElement(scoped.row.eventName)">编辑</el-button>
                        <el-button class="BTN" type="danger" size="large" @click="deleteElement(scoped.row.eventName)">删除</el-button>
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
                <button class="add_button" @click="AddElement">{{canadd}}</button>
                <button class="add_button" @click="close">取消</button>
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
  overflow: hidden; /* 去掉页面滚动条 */
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

/* 表格区域 —— 从上到下，百分比宽 */
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

/* 添加事件按钮 —— 靠左 */
#addElement {
  width: 8%;
  min-width: 100px;
  height: 5%;
  min-height: 34px;
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

/* ========== 添加/编辑弹窗 居中 ========== */
.addElement_container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 520px;
  height: auto;
  max-height: 90vh;
  background-color: #ffffff;
  border: 1px solid #e5b3a1;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  z-index: 999;
  padding: 2% 2% 3%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-y: auto;
  scrollbar-width: none;
}
.addElement_container::-webkit-scrollbar {
  display: none; /* 去掉弹窗滚动条 */
}

#addElement_title {
  font-size: clamp(16px, 3vh, 20px);
  font-weight: 600;
  color: #855ce5;
  margin-bottom: 2%;
  text-align: center;
}

.s {
  width: 90%;
  font-size: clamp(13px, 2vh, 15px);
  font-weight: 500;
  color: #5d4037;
  margin: 1% 0 0.5%;
  text-align: left;
}
.S {
  width: 90%;
  font-size: clamp(10px, 1.5vh, 12px);
  color: #8d6e63;
  margin: 0 0 1%;
  text-align: left;
}

.textinput,
.time,
.select,
.textareaInput {
  width: 90%;
  height: 5vh;
  border: 1px solid #d1c7c2;
  border-radius: 6px;
  padding: 0 1%;
  font-size: clamp(12px, 1.8vh, 14px);
  background-color: #fffcf9;
  box-sizing: border-box;
  margin-bottom: 1%;
  outline-color: #855ce5;
}

.textareaInput {
  height: 10vh;
  resize: none;
  padding: 1%;
}

#choice_container {
  width: 90%;
  display: flex;
  justify-content: center;
  gap: 2%;
  margin-top: 3%;
}

.add_button {
  width: 20%;
  min-width: 80px;
  height: 5vh;
  min-height: 34px;
  font-size: clamp(12px, 1.8vh, 15px);
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: 0.2s;
}
.add_button:first-child {
  background-color: #855ce5;
  color: #fff;
}
.add_button:first-child:hover {
  background-color: #724bd1;
}
.add_button:last-child {
  background-color: #d7ccc8;
  color: #333;
}
.add_button:last-child:hover {
  background-color: #c8b4ac;
}

.BTN {
  margin: 0 6px !important;
}
</style>