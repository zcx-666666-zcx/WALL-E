<script setup>
  import {ref , onMounted} from 'vue';
  import { GetMachineListApi } from '../../api/users';
  import { useRoute } from 'vue-router';
  import { GetIdApi } from '../../api/users';
  import router from '../../router';

  const route = useRoute()
  let userid=ref(0);
  let userName = ref('')

  onMounted(()=>{
    userName.value = route.query.username || '';
    console.log(userName.value);
    getId();
    //getMachinesList(); 
  })

  const getId = async()=>{
    const username = userName.value
    const result = await GetIdApi(username);
    if(result && result.code === 1){
      userid.value = result.data.id;
      console.log(userid.value);
      localStorage.setItem('Id',userid.value);
      getMachinesList(); 
      return;
    }
    alert("获取用户Id失败")
  }

  const getMachinesList = async()=>{
    const userId = userid.value;
    const result = await GetMachineListApi(userId);
    if(result && result.code === 1){
            if(result.data && result.data.rows && result.data.rows.length > 0){
                Machines.value = result.data.rows;
                console.log(Machines)
                return;
            }
            else{
                Machines.value = [];
                return;
            }
        }
        else{
            alert("获取表格数据失败")
            return;
        }
  }

  /*const goToPageUser = () => {
    const user = {username: userName.value,userId: userid.value}
    router.push({
      path: '/user',
      query: { userId: user.userId }
    });
  };
  const goToPageEvent = () => {
    const user = {username: userName.value,userId: userid.value}
    router.push({
      path: '/elementlist',
      query: { userId: user.userId }
    });
  };
  const goToPageMachine = () => {
    const user = {username: userName.value,userId: userid.value}
    router.push({
      path: '/machines',
      query: { userId: user.userId }
    });
  };*/


  const goToPage = (machine) => {
    console.log('选择的机器:', machine.machines);
    router.push({
      path: '/command',
      query: { machineName: machine.machines }
    });
  };

  const Machines = ref([])

</script>

<template>
  <div class="common-layout">
    <el-container>
      <el-aside width="200px" class="aside">
        <el-menu router>

            <el-menu-item index="/index" id="Index">首页</el-menu-item>

            <el-menu-item index="/elementlist" class="options" >事件管理</el-menu-item>

            <el-menu-item index="/Agent" class="options">AI设置</el-menu-item>

            <el-sub-menu class="choice",index="contacts">
              <template #title>
                <div class="title">联系人与设备</div>
              </template>
              <el-menu-item index="/user" class="Soptions" >联系人</el-menu-item>
              <el-menu-item index="/machines" class="Soptions" >设备</el-menu-item>
            </el-sub-menu>
            

            <el-sub-menu class="choice",index="command">
              <template #title>
                <div class="title" @click="getMachinesList">命令查询</div>
              </template>
              <el-menu-item @click="goToPage(MACHINES)" v-for="MACHINES in Machines"
              :key="MACHINES" 
              index="/command"
              class="Soptions"
              >{{ MACHINES.machines }}
              </el-menu-item>
            </el-sub-menu>

            <el-menu-item index="/video" class="options">视频通话</el-menu-item>

            <el-menu-item index="/drive" class="options">远程遥控</el-menu-item>

            <el-menu-item index="/connections" class="options">更多连接</el-menu-item>

            <el-menu-item index="/set" class="options">设置</el-menu-item>

            <el-menu-item index="/info" class="options">说明</el-menu-item>
            <el-menu-item index="/Agent" class="user">{{userName}}</el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="head">智 能 陪 伴 机 器 人 网 页 资 源 控 制 平 台</el-header>

        <el-main class="main">
          <router-view></router-view>
        </el-main>

      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
  template{
    height: 1300px;
    width: 2500px;
    background-color: white;
  }
  .aside{
    height: 1300px;
  }
  .user{
    border-top: 1px solid rgb(223, 242, 255);
    font-size: 20px;
    font-weight: 600;
    padding: 20px;
    height: 80px;
    opacity: 1;
    background-color: rgb(255, 241, 241);
    color: rgb(255, 0, 0);
  }
  .common-layout{
    background-size: cover;
    height: 1300px;
    width: 2500px;
    background-image: url("http://localhost:8080/images/index_picture.png");
  }
  .choice{
    border-top: 1px solid rgb(223, 242, 255);
    font-size: 20px;
    padding: 5px;
    opacity: 1;
    background-color: rgb(209, 209, 209);
  }
  .title{
    font-size: 18px;
    font-weight: 600;
  }
  .options{
    border-top: 1px solid rgb(223, 242, 255);
    font-size: 20px;
    padding: 20px;
    height: 80px;
    opacity: 1;
    background-color: rgb(209, 209, 209);
  }
  .Soptions{
    border-top: 1px solid rgb(223, 242, 255);
    font-size: 14px;
    padding: 20px;
    height: 60px;
    opacity: 1;
    background-color: rgb(235, 235, 235);
  }
  #Index{
    height: 130px;
    background-color: rgb(90, 90, 90);
    font-size: 30px;
    color: rgb(214, 214, 214);
  }
  .head{
    width: 2300px;
    height: 130px;
    margin: 0;
    background-color: rgb(155, 155, 155);
    opacity: 0.5;
    display: flex;
    justify-content: center;
    text-align: center;
    align-items: center;
    font-size: 45px;
    font-weight: 700;
    color: rgb(34, 0, 185);
    
  }
  .main{
    width: 2300px;
    height: 1170px;
    margin: 0;
    background-color: rgb(214, 214, 214);
    opacity: 0.8;
  }
</style>