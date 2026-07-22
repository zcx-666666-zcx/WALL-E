<script setup>
  import { ref, onMounted, onUnmounted, computed } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { ElMessage } from 'element-plus';
  import { GetIdApi, GetMachineListApi, GetDeviceNetworkStatusApi } from '../../api/users';
  import { logoutLocally } from '../../utils/authSession';
  import { getRobotHttpPort } from '../../utils/systemConfig';
  import { selectPreferredMachine } from '../drive/machineSelection.mjs';
  import { buildDirectRobotControlUrl } from '../drive/directRobotControl.mjs';

  const route = useRoute();
  const router = useRouter();
  let userid = ref(0);
  let userName = ref('');
  let attention = ref(false);
  let highlight = ref('提示：疑似');
  let danger = ref('摔倒');
  let sidebarOpen = ref(false);
  let isMobile = ref(false);
  let now = ref(new Date());
  let clockTimer = null;

  const Machines = ref([]);

  const getLoginUser = () => {
    try {
      return JSON.parse(localStorage.getItem('loginUserObject'))
    } catch {
      return null
    }
  }

  const isAdmin = computed(() => {
    return getLoginUser()?.role === 'admin'
  });

  onMounted(() => {
    const loginUser = getLoginUser();
    userName.value = route.query.username || loginUser?.username || '';
    if (loginUser?.id) {
      userid.value = loginUser.id;
      localStorage.setItem('Id', loginUser.id);
      getMachinesList();
    } else {
      getId();
    }
    checkScreen();
    window.addEventListener('resize', checkScreen);
    clockTimer = setInterval(() => { now.value = new Date(); }, 1000);
  });

  onUnmounted(() => {
    window.removeEventListener('resize', checkScreen);
    if (clockTimer) clearInterval(clockTimer);
  });

  const checkScreen = () => {
    isMobile.value = window.innerWidth < 768;
    if (!isMobile.value) sidebarOpen.value = false;
  };

  const toggleSidebar = () => { sidebarOpen.value = !sidebarOpen.value; };
  const closeSidebar = () => { sidebarOpen.value = false; };

  const timeStr = computed(() => {
    const d = now.value;
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  });

  const dateStr = computed(() => {
    const d = now.value;
    return d.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'short' });
  });

  const breadcrumb = computed(() => {
    const map = {
      '/index': '首页',
      '/elementlist': '事件管理',
      '/Agent': 'AI 设置',
      '/new_agent': 'AI 设置(测试)',
      '/user': '联系人',
      '/machines': '设备管理',
      '/command': '命令查询',
      '/video': '远程监护',
      '/webrtc-video': '远程监护',
      '/healthy': '健康监测',
      '/drive': '远程遥控',
      '/drive-cloud': '远程遥控（云端备份）',
      '/voice': '音色克隆',
      '/connections': '更多连接',
      '/set': '设置',
      '/robot-showcase': '机器人展示',
      '/info': '说明',
      '/admin': '系统配置',
    };
    return map[route.path] || '';
  });

  const getId = async () => {
    if (!userName.value) return;
    const result = await GetIdApi(userName.value);
    if (result && result.code === 1) {
      userid.value = result.data.id;
      localStorage.setItem('Id', userid.value);
      getMachinesList();
    }
  };

  const getMachinesList = async () => {
    const result = await GetMachineListApi(userid.value);
    if (result && result.code === 1) {
      Machines.value = result.data?.rows?.length > 0 ? result.data.rows : [];
    }
  };

  const goToPage = (machine) => {
    router.push({ path: '/command', query: { machineName: machine.machines } });
    closeSidebar();
  };

  const GoToCheck = () => {
    attention.value = false;
    router.push('/healthy');
  };

  const navTo = (path) => {
    router.push(path);
    closeSidebar();
  };

  const openDirectRobotControl = async () => {
    const machine = selectPreferredMachine(Machines.value);
    if (!machine) {
      ElMessage.warning('未找到机器人设备，已打开云端备用遥控页');
      navTo('/drive-cloud');
      return;
    }

    let networkStatus = null;
    if (machine.connectionId) {
      try {
        const result = await GetDeviceNetworkStatusApi(machine.connectionId);
        if (result?.code === 1) networkStatus = result.data;
      } catch {
        networkStatus = null;
      }
    }

    const url = buildDirectRobotControlUrl(machine, networkStatus, getRobotHttpPort());
    if (!url) {
      ElMessage.warning('未获取到机器人 IP，已打开云端备用遥控页');
      navTo('/drive-cloud');
      return;
    }

    closeSidebar();
    window.location.assign(url);
  };

  const logout = () => {
    logoutLocally()
    router.replace('/login')
  }

  const menuItems = [
    { path: '/index', icon: 'HomeFilled', label: '首页', class: 'menu-home' },
    { type: 'label', label: '功能模块' },
    { path: '/elementlist', icon: 'Notebook', label: '事件管理' },
    { path: '/Agent', icon: 'Cpu', label: 'AI 设置' },
    { path: '/new_agent', icon: 'Cpu', label: 'AI 设置(测试)' },
    { type: 'label', label: '资源管理' },
    { path: '/user', icon: 'User', label: '联系人' },
    { path: '/machines', icon: 'Monitor', label: '设备管理' },
    { path: '/command', icon: 'List', label: '命令查询' },
    { type: 'label', label: '监护功能' },
    { path: '/video', icon: 'VideoCamera', label: '远程监护' },
    { path: '/drive', icon: 'Switch', label: '远程遥控', action: openDirectRobotControl },
    { path: '/voice', icon: 'Microphone', label: '音色克隆' },
    { path: '/healthy', icon: 'CirclePlusFilled', label: '健康监测' },
    { type: 'label', label: '系统' },
    { path: '/robot-showcase', icon: 'Cpu', label: '机器人展示' },
    { path: '/connections', icon: 'Link', label: '更多连接' },
    { path: '/set', icon: 'Setting', label: '设置' },
    { path: '/admin', icon: 'Tools', label: '系统配置', adminOnly: true },
    { path: '/info', icon: 'Tickets', label: '说明' },
  ];

  const visibleMenuItems = computed(() => menuItems.filter((item) => !item.adminOnly || isAdmin.value));

  const isActive = (path) => route.path === path;
</script>

<template>
  <!-- 报警弹窗 -->
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

    <!-- 移动端汉堡按钮 -->
    <button class="hamburger" v-if="isMobile" @click="toggleSidebar">
      <span></span><span></span><span></span>
    </button>

    <!-- 移动端遮罩 -->
    <transition name="mask-fade">
      <div class="sidebar-overlay" v-if="sidebarOpen && isMobile" @click="closeSidebar"></div>
    </transition>

    <!-- ═══════════ 侧边栏 ═══════════ -->
    <aside :class="['aside', { 'aside-open': sidebarOpen }]">

      <!-- Logo -->
      <div class="logo-area">
        <div class="logo-icon">
          <svg width="20" height="20" viewBox="0 0 32 32" fill="none">
            <path d="M16 4C10 4 5 8.5 5 14c0 8 11 16 11 16s11-8 11-16c0-5.5-5-10-11-10z" fill="rgba(255,255,255,0.25)" stroke="white" stroke-width="1.8"/>
            <path d="M10 15h3.5l2-5 3 10 2-5H23" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="logo-text">
          <span class="logo-main">智伴平台</span>
          <span class="logo-sub">Companion Robot Center</span>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav class="side-nav">
        <template v-for="(item, i) in visibleMenuItems" :key="i">

          <div v-if="item.type === 'label'" class="nav-label">{{ item.label }}</div>

          <div
            v-else
            class="nav-item"
            :class="{
              'nav-item--home': item.class === 'menu-home',
              'nav-item--active': isActive(item.path),
            }"
            @click="item.action ? item.action() : navTo(item.path)"
          >
            <div class="nav-item-icon">
              <el-icon :size="18"><component :is="item.icon" /></el-icon>
            </div>
            <span class="nav-item-label">{{ item.label }}</span>
            <div v-if="isActive(item.path)" class="nav-item-indicator"></div>
          </div>

        </template>
      </nav>

      <!-- 子菜单：命令查询设备列表 -->
      <div class="nav-sub-section" v-if="Machines.length > 0">
        <div class="nav-label">已绑定设备</div>
        <div
          v-for="m in Machines"
          :key="m.id || m.machines"
          class="nav-sub-item"
          :class="{ 'nav-sub-item--active': route.query.machineName === m.machines }"
          @click="goToPage(m)"
        >
          <span class="nav-sub-dot"></span>
          {{ m.machines }}
        </div>
      </div>

      <!-- 底部用户区 -->
      <div class="aside-footer">
        <div class="aside-footer-avatar">{{ userName ? userName[0] : 'U' }}</div>
        <div class="aside-footer-text">
          <span class="aside-footer-name">{{ userName || '用户' }}</span>
          <span class="aside-footer-hint" @click="logout">退出登录</span>
        </div>
      </div>
    </aside>

    <!-- ═══════════ 右侧主体 ═══════════ -->
    <div class="right-area">

      <!-- Header -->
      <header class="head">
        <div class="head-left">
          <div class="head-breadcrumb">
            <svg width="13" height="13" viewBox="0 0 13 13" fill="none" style="flex-shrink:0">
              <path d="M1.5 6.5h10M6.5 1.5l5 5-5 5" stroke="rgba(255,255,255,0.5)" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="breadcrumb-current">{{ breadcrumb || '首页' }}</span>
          </div>
          <h1 class="head-title">{{ breadcrumb || '智能陪伴机器人控制平台' }}</h1>
        </div>
        <div class="head-right">
          <!-- 通知铃铛 -->
          <div class="head-notify">
            <svg width="17" height="17" viewBox="0 0 17 17" fill="none">
              <path d="M8.5 2.5A4.5 4.5 0 004 7v2.5L2.5 11v1h12v-1L13 9.5V7a4.5 4.5 0 00-4.5-4.5z" stroke="white" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M10 13a1.5 1.5 0 01-3 0" stroke="white" stroke-width="1.3"/>
            </svg>
            <span class="notify-dot"></span>
          </div>
          <!-- 时钟 -->
          <div class="head-clock">
            <span class="clock-time">{{ timeStr }}</span>
            <span class="clock-date">{{ dateStr }}</span>
          </div>
          <!-- 状态 -->
          <div class="head-status">
            <span class="status-dot"></span>
            <span class="status-text">运行中</span>
          </div>
        </div>
        <!-- 装饰光晕 -->
        <div class="head-glow"></div>
      </header>

      <!-- 内容区 -->
      <main class="main">
        <router-view v-slot="{ Component, route: r }">
          <transition name="page" mode="out-in">
            <component :is="Component" :key="r.path" />
          </transition>
        </router-view>
      </main>

    </div>
  </div>
</template>

<style scoped>
/* ═══════════ 根 ═══════════ */
.common-layout {
  display: flex; height: 100vh; width: 100vw;
  background: #FDF6F1;
  overflow: hidden;
}

/* 背景纹理 */
.common-layout::before {
  content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 0; opacity: 0.35;
  background-image: radial-gradient(circle, rgba(255,140,90,0.06) 1px, transparent 1px);
  background-size: 28px 28px;
}

/* 汉堡按钮 */
.hamburger {
  position: fixed; top: 14px; left: 14px; z-index: 1100;
  width: 40px; height: 40px; border-radius: 12px;
  background: var(--grad-primary);
  border: none; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
  box-shadow: var(--shadow-btn);
  transition: transform 0.2s;
}
.hamburger:active { transform: scale(0.94); }
.hamburger span { display: block; width: 18px; height: 2px; background: white; border-radius: 1px; }

.sidebar-overlay {
  position: fixed; inset: 0; z-index: 998;
  background: rgba(30, 10, 4, 0.45); backdrop-filter: blur(6px);
}

/* ═══════════ 侧边栏 ═══════════ */
.aside {
  width: var(--sidebar-w); height: 100vh; flex-shrink: 0;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(20px);
  border-right: 1px solid rgba(255, 160, 120, 0.15);
  box-shadow: 2px 0 24px rgba(180, 80, 30, 0.06);
  display: flex; flex-direction: column;
  position: relative; z-index: 999;
  transition: transform 0.32s var(--ease-smooth);
}

/* Logo */
.logo-area {
  display: flex; align-items: center; gap: 11px;
  padding: 22px 18px 18px;
  border-bottom: 1px solid rgba(255, 150, 100, 0.1);
  flex-shrink: 0;
}
.logo-icon {
  width: 42px; height: 42px; border-radius: 14px;
  background: var(--grad-primary);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; color: white;
  box-shadow: 0 4px 14px rgba(255, 90, 46, 0.3);
}
.logo-text { display: flex; flex-direction: column; }
.logo-main { font-size: 16px; font-weight: 800; color: var(--c-text-heading); letter-spacing: 0.01em; line-height: 1.2; }
.logo-sub { font-size: 9.5px; color: var(--c-text-muted); letter-spacing: 0.04em; text-transform: uppercase; }

/* 导航菜单 */
.side-nav {
  flex: 1; overflow-y: auto; padding: 10px 10px 4px;
  display: flex; flex-direction: column; gap: 2px;
}
.side-nav::-webkit-scrollbar { width: 0; }

.nav-label {
  font-size: 9.5px; font-weight: 700; color: var(--c-text-ghost);
  letter-spacing: 0.1em; text-transform: uppercase;
  padding: 14px 12px 6px;
}

.nav-item {
  display: flex; align-items: center; gap: 10px;
  height: 44px; padding: 0 12px; border-radius: var(--radius-sm);
  cursor: pointer; transition: all 0.22s var(--ease-smooth);
  position: relative; overflow: hidden;
  color: var(--c-text-secondary);
  font-size: 13.5px; font-weight: 500;
}
.nav-item:hover {
  background: rgba(255, 140, 90, 0.07);
  color: var(--c-primary);
  transform: translateX(2px);
}
.nav-item--active {
  background: rgba(255, 140, 90, 0.1) !important;
  color: var(--c-primary) !important;
  font-weight: 700 !important;
}

.nav-item-icon {
  width: 34px; height: 34px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: all 0.22s var(--ease-smooth);
  background: transparent;
}
.nav-item--active .nav-item-icon {
  background: var(--grad-primary);
  color: white;
  box-shadow: 0 3px 10px rgba(255, 90, 46, 0.25);
}
.nav-item--active .nav-item-icon :deep(.el-icon) { color: white; }

.nav-item-indicator {
  position: absolute; right: 0; top: 50%; transform: translateY(-50%);
  width: 3px; height: 18px; border-radius: 2px;
  background: var(--c-primary);
  animation: scaleIn 0.25s var(--ease-bounce);
}

/* 首页特殊样式 */
.nav-item--home {
  background: var(--grad-primary) !important;
  color: white !important; font-weight: 700 !important;
  box-shadow: 0 4px 14px rgba(255, 90, 46, 0.3);
  margin-bottom: 4px;
}
.nav-item--home:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(255, 90, 46, 0.4);
}
.nav-item--home .nav-item-icon { background: rgba(255,255,255,0.2); }
.nav-item--home .nav-item-icon :deep(.el-icon) { color: white; }

/* 设备子菜单 */
.nav-sub-section {
  border-top: 1px solid rgba(255, 150, 100, 0.1);
  padding: 8px 10px 12px; flex-shrink: 0;
}
.nav-sub-item {
  display: flex; align-items: center; gap: 8px;
  height: 36px; padding: 0 12px; border-radius: 8px;
  font-size: 12.5px; color: var(--c-text-secondary);
  cursor: pointer; transition: all 0.2s;
}
.nav-sub-item:hover { background: rgba(255, 140, 90, 0.06); color: var(--c-primary); }
.nav-sub-item--active { color: var(--c-primary); font-weight: 600; background: rgba(255, 140, 90, 0.08); }
.nav-sub-dot {
  width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0;
  background: var(--c-text-ghost);
  transition: all 0.2s;
}
.nav-sub-item--active .nav-sub-dot { background: var(--c-primary); box-shadow: 0 0 6px rgba(255,90,46,0.4); }

/* 底部用户 */
.aside-footer {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 18px;
  border-top: 1px solid rgba(255, 150, 100, 0.1);
  flex-shrink: 0;
}
.aside-footer-avatar {
  width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
  background: var(--grad-warm);
  color: var(--c-primary); font-weight: 800; font-size: 14px;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 8px rgba(255, 140, 90, 0.2);
}
.aside-footer-text { display: flex; flex-direction: column; }
.aside-footer-name { font-size: 13px; font-weight: 700; color: var(--c-text); }
.aside-footer-hint { font-size: 11px; color: var(--c-text-muted); cursor: pointer; transition: color 0.2s; }
.aside-footer-hint:hover { color: var(--c-danger); }

/* ═══════════ 右侧 ═══════════ */
.right-area {
  flex: 1; display: flex; flex-direction: column;
  min-width: 0; position: relative; z-index: 1;
}

/* Header */
.head {
  height: 72px; flex-shrink: 0;
  background: linear-gradient(105deg, #FF7A50 0%, #FF5A2E 40%, #E8451A 100%);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 32px; position: relative; overflow: hidden;
  box-shadow: 0 2px 16px rgba(200, 60, 20, 0.18);
}
.head-glow {
  position: absolute; top: -80px; right: -40px;
  width: 240px; height: 240px; border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
  pointer-events: none;
}

.head-left { display: flex; flex-direction: column; gap: 0; position: relative; z-index: 1; }
.head-breadcrumb {
  display: flex; align-items: center; gap: 6px; margin-bottom: 2px;
}
.breadcrumb-current {
  font-size: 11px; color: rgba(255,255,255,0.55);
  letter-spacing: 0.06em; font-weight: 500;
}
.head-title {
  font-size: 19px; font-weight: 800; color: white;
  letter-spacing: 0.02em; margin: 0;
  text-shadow: 0 1px 3px rgba(160, 30, 0, 0.2);
}

.head-right { display: flex; align-items: center; gap: 18px; position: relative; z-index: 1; }

.head-notify {
  width: 38px; height: 38px; border-radius: 50%;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.18);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; position: relative; transition: background 0.2s;
}
.head-notify:hover { background: rgba(255,255,255,0.22); }
.notify-dot {
  position: absolute; top: 8px; right: 8px;
  width: 7px; height: 7px; border-radius: 50%;
  background: #FFD54F;
  box-shadow: 0 0 6px rgba(255, 213, 79, 0.6);
  animation: blink 2.5s ease infinite;
}

.head-clock {
  display: flex; flex-direction: column; align-items: flex-end;
}
.clock-time { font-size: 16px; font-weight: 700; color: white; letter-spacing: 0.04em; line-height: 1.1; }
.clock-date { font-size: 10.5px; color: rgba(255,255,255,0.55); letter-spacing: 0.05em; font-weight: 500; }

.head-status {
  display: flex; align-items: center; gap: 6px;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 100px; padding: 6px 14px;
}
.status-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #9DFFB0;
  box-shadow: 0 0 8px rgba(157, 255, 176, 0.7);
  animation: blink 2s ease infinite;
}
.status-text { font-size: 11.5px; color: rgba(255,255,255,0.85); letter-spacing: 0.04em; font-weight: 500; }

/* 内容区 */
.main {
  flex: 1; background: transparent;
  padding: 20px 24px; box-sizing: border-box;
  overflow: auto; position: relative; z-index: 1;
  min-height: 0;
  container-type: inline-size;
}

.main :deep(> *) {
  max-width: 1440px;
  margin-left: auto;
  margin-right: auto;
}

/* ═══════════ 报警弹窗 ═══════════ */
#attention {
  position: fixed; top: 50%; left: 50%; transform: translate(-50%,-50%);
  z-index: 1001; width: 340px; background: white; border-radius: 24px;
  padding: 32px 28px 24px;
  box-shadow: 0 0 0 1px rgba(255,100,60,0.12), 0 24px 64px rgba(160, 40, 10, 0.2);
  display: flex; flex-direction: column; align-items: center; gap: 14px; text-align: center;
}
.alert-icon-wrap {
  width: 60px; height: 60px; border-radius: 50%;
  background: #FFF4EF; border: 2px solid #FFD4BF;
  display: flex; align-items: center; justify-content: center;
  color: var(--c-primary); flex-shrink: 0;
  animation: pulse-glow 2s ease infinite;
}
.alert-text { display: flex; flex-direction: column; gap: 4px; font-size: 14px; color: var(--c-text); line-height: 1.6; }
.alert-highlight { font-size: 12px; font-weight: 700; color: var(--c-primary); letter-spacing: 0.06em; }
.alert-text strong { color: var(--c-danger); font-weight: 800; }
#check {
  width: 100%; height: 44px; font-size: 14px; font-weight: 700; font-family: inherit;
  background: var(--grad-primary-h); color: white;
  border: none; border-radius: 12px; cursor: pointer; letter-spacing: 0.04em;
  transition: all 0.25s ease; box-shadow: var(--shadow-btn);
}
#check:hover { transform: translateY(-2px); box-shadow: var(--shadow-btn-hover); }
#check:active { transform: scale(0.97); }

/* ═══════════ 过渡 ═══════════ */
.alert-fade-enter-active { animation: alertIn 0.35s var(--ease-bounce); }
.alert-fade-leave-active { animation: alertOut 0.25s ease forwards; }
@keyframes alertIn {
  from { opacity:0; transform:translate(-50%,-54%) scale(0.9); }
  to   { opacity:1; transform:translate(-50%,-50%) scale(1); }
}
@keyframes alertOut { to { opacity:0; transform:translate(-50%,-46%) scale(0.95); } }

.mask-fade-enter-active, .mask-fade-leave-active { transition: opacity 0.25s; }
.mask-fade-enter-from, .mask-fade-leave-to { opacity: 0; }

/* 页面切换 */
.page-enter-active { animation: pageIn 0.28s var(--ease-smooth); }
.page-leave-active { animation: pageOut 0.18s var(--ease-smooth); }

/* ═══════════ 响应式 ═══════════ */
@media (max-width: 768px) {
  .aside {
    position: fixed; left: 0; top: 0; z-index: 999;
    transform: translateX(-100%);
  }
  .aside.aside-open { transform: translateX(0); }
  .head { padding: 0 12px 0 56px; }
  .head-title { font-size: 14px; }
  .head-clock, .head-notify { display: none; }
  .main { padding: 12px; overflow-x: hidden; }
}

@media (min-width: 1440px) {
  .main { padding: 24px 32px; }
}
</style>
