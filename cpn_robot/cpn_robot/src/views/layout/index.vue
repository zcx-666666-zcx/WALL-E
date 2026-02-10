<script setup>
  import {ref , onMounted} from 'vue';
  import { useRoute } from 'vue-router';
  import { GetIdApi } from '../../api/users';
  import { GetMachineListApi } from '../../api/users';
  import router from '../../router';

  const route = useRoute()
  let userid=ref(0);
  let userName = ref('');
  let attention = ref(true);
  let highlight = ref('提示：疑似');
  let danger = ref('摔倒')

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

  const goToWalleInterface = () => {
    // 跳转到 walle-replica 的 web_interface 界面
    window.open('http://192.168.3.54:5000', '_blank');
  };

  //const goToWebrtcVideo = () => {
    // 跳转到WebRTC视频通话页面
  //  router.push('/webrtc-video');
  //};

  const GoToCheck = ()=>{
    attention.value=false;
    router.push('/healthy');
  }

  const Machines = ref([])
</script>

<template>
  <div id="attention" v-if="attention"><el-icon :size="40"><WarnTriangleFilled /></el-icon>
    {{highlight}}用户存在{{danger}}情况
    <button id="check" @click="GoToCheck">查看</button>
  </div>
  <div class="common-layout">
    <el-container>
      <el-aside width="200px" class="aside">
        <el-menu router>
            <el-menu-item index="/index" id="Index"><el-icon :size="80"><HomeFilled /></el-icon>首页</el-menu-item>
            <el-menu-item index="/elementlist" class="options" ><el-icon :size="50"><Notebook /></el-icon>事件管理</el-menu-item>
            <el-menu-item index="/Agent" class="options"><el-icon :size="50"><Cpu /></el-icon>AI设置</el-menu-item>

            <el-sub-menu class="choice" index="contacts">
              <template #title>
                <div class="title">联系人与设备</div>
              </template>
              <el-menu-item index="/user" class="Soptions" >联系人</el-menu-item>
              <el-menu-item index="/machines" class="Soptions" >设备</el-menu-item>
            </el-sub-menu>
            

            <el-sub-menu class="choice" index="command">
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

            <el-menu-item index="/video" class="options"><el-icon :size="50"><VideoCamera /></el-icon>视频通话</el-menu-item>
            <el-menu-item index="/drive" class="options"><el-icon :size="50"><Switch /></el-icon>远程遥控</el-menu-item>
            <el-menu-item index="/healthy" class="options"><el-icon :size="50"><CirclePlusFilled /></el-icon>健康监测</el-menu-item>
            <el-menu-item index="/connections" class="options"><el-icon :size="50"><Link /></el-icon>更多连接</el-menu-item>
            <el-menu-item index="/set" class="options"><el-icon :size="50"><Setting /></el-icon>设置</el-menu-item>
            <el-menu-item index="/info" class="options"><el-icon :size="50"><List /></el-icon>说明</el-menu-item>
            <el-menu-item @click="goToWalleInterface" class="options">WALL-E原版界面</el-menu-item>            
            <el-menu-item index="/login" class="user">{{userName}}-退出登录</el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="head">
          智 能 陪 伴 机 器 人 网 页 资 源 控 制 平 台
          <el-button type="primary" size="small" class="walle-jump-btn" @click="goToWalleInterface">WALL-E原版界面</el-button>
        </el-header>

        <el-main class="main">
          <router-view></router-view>
        </el-main>

      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
#attention{
  width: 30%;
  height: 20%;
  background-color: rgb(255, 255, 255);
  position: absolute;
  top: 7%;
  left: 35%;
  z-index: 111;
  border: 5px solid rgb(72, 72, 72);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  font-size: 1.4vw;
  font-weight: 600;
  color: red;
  opacity: 0.85;
}
#check{
  width: 30%;
  height: 30%;
  font-size: 1.1vw;
  background-color: rgb(255, 66, 66);
  color: white;
  font-weight: 600;
  border: 0;
}
:deep(html), :deep(body) {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden;
}
template {
  height: 100vh;
  width: 100vw;
  background-color: white;
}
.aside {
  height: 100vh !important;
  width: 250px !important;
  background-color: white;
}
.user {
  border-top: 1px solid rgb(223, 242, 255);
  font-size: 22px;
  font-weight: 600;
  padding: 20px;
  height: 100px;
  opacity: 1;
  background-color: rgb(255, 241, 241);
  color: rgb(255, 0, 0);
}
.common-layout {
  background-size: cover;
  background-position: center;
  height: 100vh;
  width: 100vw;
  background-image: url("http://localhost:8080/images/index_picture.png");
  box-sizing: border-box;
}
.choice {
  /*border-top: 1px solid rgb(223, 242, 255);*/
  font-size: 22px;
  padding: 5px;
  opacity: 1;
  background-color: rgb(209, 209, 209);
}
.title {
  font-size: 20px;
  font-weight: 600;
}
.options {
  /*border-top: 1px solid rgb(223, 242, 255);*/
  font-size: 22px;
  padding: 20px;
  height: 100px;
  opacity: 1;
  background-color: rgb(209, 209, 209);
}
.Soptions {
  /*border-top: 1px solid rgb(223, 242, 255);*/
  font-size: 16px;
  padding: 20px;
  height: 75px;
  opacity: 1;
  background-color: rgb(235, 235, 235);
}
#Index {
  height: 130px;
  background-color: rgb(90, 90, 90);
  font-size: 30px;
  color: rgb(214, 214, 214);
}
.head {
  width: calc(100vw - 250px);
  height: 130px;
  margin: 0;
  background-color: rgb(155, 155, 155);
  opacity: 0.5;
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  font-size: 45px;
  font-weight: 700;
  color: rgb(34, 0, 185);
}
.walle-jump-btn {
  margin-right: 20px;
  height: 40px;
  font-size: 16px;
  font-weight: 600;
}
.main {
  width: calc(100vw - 250px);
  height: calc(100vh - 130px);
  margin: 0;
  background-color: rgb(214, 214, 214);
  opacity: 0.8;
  box-sizing: border-box;
}
</style>