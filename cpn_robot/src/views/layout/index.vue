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
    getId();
  })

  const getId = async()=>{
    const result = await GetIdApi(userName.value);
    if(result && result.code === 1){
      userid.value = result.data.id;
      localStorage.setItem('Id', userid.value);
      getMachinesList();
      return;
    }
    alert("获取用户Id失败")
  }

  const getMachinesList = async()=>{
    const result = await GetMachineListApi(userid.value);
    if(result && result.code === 1){
      Machines.value = result.data?.rows?.length > 0 ? result.data.rows : [];
    } else {
      alert("获取表格数据失败");
    }
  }

  const goToPage = (machine) => {
    router.push({ path: '/command', query: { machineName: machine.machines } });
  };

  const goToWalleInterface = () => {
    window.open('http://192.168.3.54:5000', '_blank');
  };

  const GoToCheck = ()=>{
    attention.value = false;
    router.push('/healthy');
  }

  const Machines = ref([])
</script>

<template>
  <transition name="alert-fade">
    <div id="attention" v-if="attention">
      <div class="alert-icon-wrap">
        <el-icon :size="28"><WarnTriangleFilled /></el-icon>
      </div>
      <div class="alert-text">
        <span class="alert-highlight">{{ highlight }}</span>
        <span>用户存在 <strong>{{ danger }}</strong> 情况</span>
      </div>
      <button id="check" @click="GoToCheck">立即查看</button>
    </div>
  </transition>

  <div class="common-layout">
    <el-container>
      <el-aside width="230px" class="aside">

        <div class="logo-area">
          <div class="logo-icon">
            <el-icon :size="22"><HomeFilled /></el-icon>
          </div>
          <div class="logo-text">
            <span class="logo-main">智伴平台</span>
            <span class="logo-sub">陪护机器人控制中心</span>
          </div>
        </div>

        <el-menu router class="side-menu">

          <el-menu-item index="/index" class="menu-home">
            <el-icon :size="18"><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>

          <div class="menu-section-label">功能模块</div>

          <el-menu-item index="/elementlist" class="options">
            <el-icon :size="18"><Notebook /></el-icon>
            <span>事件管理</span>
          </el-menu-item>

          <el-menu-item index="/Agent" class="options">
            <el-icon :size="18"><Cpu /></el-icon>
            <span>AI 设置</span>
          </el-menu-item>

          <div class="menu-section-label">资源管理</div>

          <el-sub-menu class="choice" index="contacts">
            <template #title>
              <el-icon :size="18"><User /></el-icon>
              <span>联系人与设备</span>
            </template>
            <el-menu-item index="/user" class="Soptions">联系人</el-menu-item>
            <el-menu-item index="/machines" class="Soptions">设备</el-menu-item>
          </el-sub-menu>

          <el-sub-menu class="choice" index="command">
            <template #title>
              <el-icon :size="18"><Monitor /></el-icon>
              <span>命令查询</span>
            </template>
            <el-menu-item
              @click="goToPage(MACHINES)"
              v-for="MACHINES in Machines"
              :key="MACHINES"
              index="/command"
              class="Soptions"
            >{{ MACHINES.machines }}</el-menu-item>
          </el-sub-menu>

          <div class="menu-section-label">监护功能</div>

          <el-menu-item index="/video" class="options">
            <el-icon :size="18"><VideoCamera /></el-icon>
            <span>远程监护</span>
          </el-menu-item>

          <el-menu-item index="/drive" class="options">
            <el-icon :size="18"><Switch /></el-icon>
            <span>远程遥控（测试）</span>
          </el-menu-item>

          <el-menu-item @click="goToWalleInterface" class="options">
            <el-icon :size="18"><Switch /></el-icon>
            <span>远程遥控</span>
          </el-menu-item>

          <el-menu-item index="/healthy" class="options">
            <el-icon :size="18"><CirclePlusFilled /></el-icon>
            <span>状态监测</span>
          </el-menu-item>

          <div class="menu-section-label">系统</div>

          <el-menu-item index="/connections" class="options">
            <el-icon :size="18"><Link /></el-icon>
            <span>更多连接</span>
          </el-menu-item>

          <el-menu-item index="/set" class="options">
            <el-icon :size="18"><Setting /></el-icon>
            <span>设置</span>
          </el-menu-item>

          <el-menu-item index="/info" class="options">
            <el-icon :size="18"><List /></el-icon>
            <span>说明</span>
          </el-menu-item>

          <!-- ✅ 退出登录：作为普通菜单项，彻底解决遮挡问题 -->
          <div class="menu-section-label">账号</div>

          <el-menu-item index="/login" class="user-menu-item">
            <div class="user-avatar-sm">{{ userName ? userName[0] : 'U' }}</div>
            <div class="user-menu-text">
              <span class="user-name-sm">{{ userName || '用户' }}</span>
              <span class="user-logout-hint">点击退出登录</span>
            </div>
          </el-menu-item>

        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="head">
          <div class="head-content">
            <span class="head-title">智能陪伴机器人网页资源控制平台</span>
            <div class="head-status">
              <span class="status-dot"></span>
              <span class="status-text">系统运行中</span>
            </div>
          </div>
        </el-header>
        <el-main class="main">
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
:deep(html), :deep(body) {
  margin: 0; padding: 0; height: 100%; width: 100%;
  overflow: hidden;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

.common-layout { height: 100vh; width: 100vw; background: #ffefe0; box-sizing: border-box; }

/* 侧边栏 */
.aside {
  height: 100vh !important; width: 230px !important;
  background: #FFFFFF;
  border-right: 1px solid rgba(255,160,122,0.15);
  box-shadow: 2px 0 16px rgba(200,100,60,0.06);
  display: flex; flex-direction: column; overflow: hidden;
}

.logo-area {
  display: flex; align-items: center; gap: 10px;
  padding: 20px 18px 16px;
  border-bottom: 1px solid rgba(255,160,122,0.12);
  flex-shrink: 0;
}
.logo-icon {
  width: 40px; height: 40px; border-radius: 12px;
  background: linear-gradient(135deg, #FFB899, #FF7043);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; color: white;
  box-shadow: 0 4px 12px rgba(255,112,67,0.28);
}
.logo-text { display: flex; flex-direction: column; }
.logo-main { font-size: 15px; font-weight: 700; color: #3A2820; letter-spacing: 0.02em; }
.logo-sub { font-size: 10px; color: #B08070; margin-top: 1px; letter-spacing: 0.02em; }

/* 菜单 —— 去掉 padding-bottom，让菜单项自然排布到底 */
.side-menu {
  border: none !important;
  flex: 1; overflow-y: auto;
  padding: 8px 0 12px;
  background: transparent !important;
}
.side-menu::-webkit-scrollbar { width: 0; }

.menu-section-label {
  font-size: 10px; font-weight: 600; color: #C4A898;
  letter-spacing: 0.08em; text-transform: uppercase;
  padding: 16px 20px 6px;
}

.menu-home {
  margin: 4px 12px 4px !important; border-radius: 10px !important;
  height: 48px !important; font-size: 14px !important; font-weight: 600 !important;
  color: white !important;
  background: linear-gradient(135deg, #FFB899, #FF7043) !important;
  box-shadow: 0 4px 14px rgba(255,112,67,0.25);
  transition: all 0.25s ease !important;
}
.menu-home:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 18px rgba(255,112,67,0.35) !important; }
.menu-home .el-icon { color: white !important; }

.options {
  font-size: 13.5px !important; height: 46px !important;
  margin: 2px 12px !important; border-radius: 10px !important;
  color: #5A3828 !important; transition: all 0.2s ease !important;
  background: transparent !important;
}
.options:hover { background: #FFF0E8 !important; color: #E05A30 !important; transform: translateX(3px); }
:deep(.el-menu-item.is-active).options { background: #FFF0E8 !important; color: #E05A30 !important; font-weight: 600 !important; }
.options .el-icon { color: #E07050 !important; transition: 0.2s; }
.options:hover .el-icon { color: #E05A30 !important; }

:deep(.el-sub-menu__title) {
  font-size: 13.5px !important; height: 46px !important;
  margin: 2px 12px !important; border-radius: 10px !important;
  color: #5A3828 !important; padding-right: 12px !important;
}
:deep(.el-sub-menu__title:hover) { background: #FFF0E8 !important; color: #E05A30 !important; }
:deep(.el-sub-menu__title .el-icon) { color: #E07050 !important; }

.Soptions {
  font-size: 13px !important; height: 40px !important;
  margin: 2px 16px 2px 24px !important; border-radius: 8px !important;
  color: #7A5040 !important; background: transparent !important;
  transition: all 0.2s ease !important;
}
.Soptions:hover { background: #FFF5F0 !important; color: #E05A30 !important; transform: translateX(2px); }

/* 退出登录菜单项 */
.user-menu-item {
  margin: 4px 12px 12px !important;
  height: 56px !important;
  border-radius: 12px !important;
  border: 1px solid rgba(255,160,122,0.2) !important;
  background: #FFF8F5 !important;
  transition: all 0.2s ease !important;
  display: flex !important; align-items: center !important; justify-content: center !important;
  gap: 10px !important; padding: 0 12px !important;
}
.user-menu-item:hover {
  background: #FFE8DC !important;
  border-color: rgba(255,130,90,0.35) !important;
}
.user-avatar-sm {
  width: 34px; height: 34px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, #FFB899, #FF8A65);
  color: white; font-weight: 700; font-size: 14px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 8px rgba(255,112,67,0.2);
}
.user-menu-text { display: flex; flex-direction: column; flex: 1;}
.user-name-sm {
  font-size: 13px; font-weight: 600; color: #3A2820;
  display: flex;
  justify-content: top;
  align-items: left;
  height: 35px !important;
}
.user-logout-hint { font-size: 11px; color: #C07060; margin-top: 1px; display: flex;
  justify-content: top;
  align-items: center; height: 35px !important;}
.user-menu-item:hover .user-logout-hint { color: #E05A30; }

/* Header */
.head {
  height: 72px !important;
  background: linear-gradient(90deg, #FF9A76, #FF7043);
  display: flex; align-items: center; padding: 0 32px;
  box-shadow: 0 2px 12px rgba(200,80,40,0.18);
  position: relative; overflow: hidden;
}
.head::before {
  content: ''; position: absolute; top: -40px; right: -40px;
  width: 180px; height: 180px; border-radius: 50%;
  background: rgba(255,255,255,0.08); pointer-events: none;
}
.head::after {
  content: ''; position: absolute; bottom: -60px; left: 30%;
  width: 140px; height: 140px; border-radius: 50%;
  background: rgba(255,255,255,0.05); pointer-events: none;
}
.head-content {
  display: flex; align-items: center; justify-content: space-between;
  width: 100%; position: relative; z-index: 1;
}
.head-title { font-size: 20px; font-weight: 700; color: white; letter-spacing: 3px; text-shadow: 0 1px 4px rgba(180,60,20,0.2); }
.head-status {
  display: flex; align-items: center; gap: 6px;
  background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25);
  border-radius: 100px; padding: 5px 14px;
}
.status-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #A8FFCA; box-shadow: 0 0 6px rgba(168,255,202,0.8);
  animation: blink 2s ease infinite;
}
.status-text { font-size: 12px; color: rgba(255,255,255,0.9); letter-spacing: 0.04em; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }

.main { background: transparent; padding: 24px; box-sizing: border-box; height: calc(100vh - 72px); }

/* 报警弹窗 */
#attention {
  position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
  z-index: 999; width: 320px; background: white; border-radius: 20px;
  padding: 28px 28px 24px;
  box-shadow: 0 0 0 1px rgba(255,120,80,0.15), 0 20px 60px rgba(200,80,40,0.18), 0 4px 16px rgba(200,80,40,0.1);
  display: flex; flex-direction: column; align-items: center; gap: 12px; text-align: center;
}
.alert-icon-wrap {
  width: 56px; height: 56px; border-radius: 50%;
  background: #FFF3EE; border: 2px solid #FFD0BC;
  display: flex; align-items: center; justify-content: center;
  color: #E05A30; flex-shrink: 0;
}
.alert-text { display: flex; flex-direction: column; gap: 4px; font-size: 14px; color: #5A3020; line-height: 1.6; }
.alert-highlight { font-size: 12px; font-weight: 600; color: #E07050; letter-spacing: 0.06em; }
.alert-text strong { color: #C0392B; font-weight: 700; }
#check {
  width: 100%; height: 42px; font-size: 14px; font-weight: 600; font-family: inherit;
  background: linear-gradient(90deg, #FF9A76, #FF6040); color: white;
  border: none; border-radius: 12px; cursor: pointer; letter-spacing: 0.04em;
  transition: all 0.25s ease; box-shadow: 0 4px 14px rgba(255,80,40,0.28);
}
#check:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(255,80,40,0.35); }

.alert-fade-enter-active { animation: alertIn 0.35s cubic-bezier(0.34,1.56,0.64,1); }
.alert-fade-leave-active { animation: alertOut 0.25s ease forwards; }
@keyframes alertIn {
  from { opacity:0; transform:translate(-50%,-54%) scale(0.9); }
  to   { opacity:1; transform:translate(-50%,-50%) scale(1); }
}
@keyframes alertOut { to { opacity:0; transform:translate(-50%,-46%) scale(0.95); } }
</style>