<script setup>
  import {ref , onMounted} from 'vue';
  import { useRoute } from 'vue-router';
  import { GetIdApi } from '../../api/users';
  import { GetMachineListApi } from '../../api/users';
  import router from '../../router';

  const route = useRoute()
  let userid=ref(0);
  let userName = ref('');
  let attention = ref(false);
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
    window.open('http://10.188.145.97:5000', '_blank');
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
            
            <el-menu-item @click="goToWalleInterface" class="options"><el-icon :size="50"><Switch /></el-icon>远程遥控</el-menu-item>
            <el-menu-item index="/healthy" class="options"><el-icon :size="50"><CirclePlusFilled /></el-icon>健康监测</el-menu-item>
            <el-menu-item index="/connections" class="options"><el-icon :size="50"><Link /></el-icon>更多连接</el-menu-item>
            <el-menu-item index="/set" class="options"><el-icon :size="50"><Setting /></el-icon>设置</el-menu-item>
            <el-menu-item index="/info" class="options"><el-icon :size="50"><List /></el-icon>说明</el-menu-item>            
            <el-menu-item index="/login" class="user">{{userName}}-退出登录</el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-header class="head">
          智 能 陪 伴 机 器 人 网 页 资 源 控 制 平 台
        </el-header>

        <el-main class="main">
          <router-view></router-view>
        </el-main>

      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
/* ===== 全局重置 ===== */
:deep(html), :deep(body) {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: hidden;
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

/* ===== 页面整体背景 ===== */
.common-layout {
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #FFF8F3, #FFEFE6);
  box-sizing: border-box;
}

/* ===== 左侧菜单 ===== */
.aside {
  height: 100vh !important;
  width: 250px !important;
  background: #FFFDFB;
  box-shadow: 4px 0 20px rgba(255, 138, 101, 0.08);
  border-right: 1px solid #FFE0D6;
}

/* 首页按钮 */
#Index {
  height: 130px;
  background: linear-gradient(135deg, #FFB199, #FF8A65);
  font-size: 30px;
  color: white;
  border-radius: 0 0 16px 16px;
}

/* 一级菜单 */
.options {
  font-size: 20px;
  padding: 18px;
  height: 90px;
  background-color: transparent;
  border-radius: 12px;
  margin: 8px;
  transition: all 0.3s ease;
}

/* hover 动效 */
.options:hover {
  background: #FFEDE5;
  transform: translateX(4px);
}

/* 子菜单 */
.Soptions {
  font-size: 15px;
  padding: 15px;
  height: 65px;
  background-color: #FFF6F2;
  margin: 6px 10px;
  border-radius: 10px;
  transition: all 0.25s ease;
}

.Soptions:hover {
  background: #FFE4D8;
  transform: translateX(3px);
}

/* 分组 */
.choice {
  font-size: 18px;
  padding: 6px;
  background-color: transparent;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #FF8A65;
}

/* 退出登录 */
.user {
  border-top: 1px solid #FFE0D6;
  font-size: 18px;
  padding: 20px;
  height: 90px;
  background-color: #FFF3EE;
  color: #E64A19;
  border-radius: 12px;
  margin: 10px;
  transition: 0.3s;
}

.user:hover {
  background-color: #FFE4D8;
}

/* ===== 顶部 Header ===== */
.head {
  width: calc(100vw - 250px);
  height: 110px;
  background: linear-gradient(90deg, #FFB199, #FF8A65);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 36px;
  font-weight: 700;
  color: white;
  letter-spacing: 4px;
  box-shadow: 0 4px 12px rgba(255, 138, 101, 0.2);
}

/* ===== 主内容区 ===== */
.main {
  width: calc(100vw - 250px);
  height: calc(100vh - 130px);
  background-color: transparent;
  padding: 20px;
  box-sizing: border-box;
}

/* 通用卡片（建议你其他页面用） */
.card {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 8px 24px rgba(255, 138, 101, 0.08);
}

/* ===== 图标统一风格 ===== */
.el-icon {
  color: #FF8A65;
  transition: 0.3s;
}

.el-menu-item:hover .el-icon {
  transform: scale(1.1);
}

/* ===== 报警弹窗 ===== */
#attention {
  width: 28%;
  height: 22%;
  background: #FFF7F5;
  position: absolute;
  top: 7%;
  left: 36%;
  z-index: 111;
  border: 2px solid #FF8A65;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 10px;
  text-align: center;
  font-size: 1.3vw;
  font-weight: 600;
  color: #D84315;
  box-shadow: 0 10px 30px rgba(255, 138, 101, 0.2);
  animation: fadeIn 0.4s ease;
}

/* 弹窗按钮 */
#check {
  width: 30%;
  height: 30%;
  font-size: 1.1vw;
  background: linear-gradient(90deg, #FF8A65, #FF7043);
  color: white;
  font-weight: 600;
  border: 0;
  border-radius: 10px;
  transition: 0.3s;
}

#check:hover {
  transform: scale(1.05);
}

/* ===== 动画 ===== */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 0.9;
    transform: translateY(0);
  }
}
</style>