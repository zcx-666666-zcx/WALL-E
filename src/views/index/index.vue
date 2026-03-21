<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

const goPage = (path) => {
  router.push(path)
}

const goToWalleInterface = () => {
    // 跳转到 walle-replica 的 web_interface 界面
    window.open('http://10.188.145.97:5000', '_blank');
  }
</script>

<template>
  <div class="container1">
    <div class="title">欢迎使用智能陪伴机器人</div>

    <div class="menu-grid">
      <div class="menu-card" @click="goPage('/elementlist')">
        <el-icon :size="80"><Notebook /></el-icon>
        <span>事件管理</span>
      </div>

      <div class="menu-card" @click="goPage('/Agent')">
        <el-icon :size="80"><Cpu /></el-icon>
        <span>AI设置</span>
      </div>

      <div class="menu-card" @click="goPage('/command')">
        <el-icon :size="80"><Notebook /></el-icon>
        <span>命令查询</span>
      </div>

      <div class="menu-card" @click="goPage('/video')">
        <el-icon :size="80"><VideoCamera /></el-icon>
        <span>视频通话</span>
      </div>

      <div class="menu-card" @click=goToWalleInterface()>
        <el-icon :size="80"><Switch /></el-icon>
        <span>远程遥控</span>
      </div>

      <div class="menu-card" @click="goPage('/healthy')">
        <el-icon :size="80"><CirclePlusFilled /></el-icon>
        <span>健康监测</span>
      </div>
    </div>
  </div>
</template>

<style>
/* ===== 主容器 ===== */
.container1 {
  height: 100%;
  width: 100%;
  background: linear-gradient(135deg, #FFF8F3, #FFEFE6);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 6vh;
  overflow: hidden;
  box-sizing: border-box;
  padding: 5vh 5vw;
}

/* ===== 标题 ===== */
.title {
  color: #E64A19;
  font-size: clamp(36px, 5vw, 56px);
  font-weight: 700;
  text-align: center;
  letter-spacing: 2px;
  margin: 0;
}

/* ===== 菜单网格 ===== */
.menu-grid {
  width: 100%;
  max-width: 820px;
  height: 52vh;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 2.2vw;
  justify-items: center;
  align-items: center;
}

/* ===== 卡片按钮（核心优化） ===== */
.menu-card {
  width: 100%;
  height: 100%;

  /* 产品感背景 */
  background: #FFFFFF;

  border-radius: 20px;

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 12px;

  font-size: 18px;
  font-weight: 600;
  color: #444;

  /* 高级阴影 */
  box-shadow: 0 10px 30px rgba(255, 138, 101, 0.12);

  cursor: pointer;
  transition: all 0.25s ease;

  border: 1px solid #FFE0D6;
  box-sizing: border-box;
}

/* 图标 */
.menu-card .el-icon {
  color: #FF8A65;
  transition: 0.3s;
}

/* hover 效果（高级感关键） */
.menu-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 15px 40px rgba(255, 138, 101, 0.25);
  background: #FFF7F3;
}

/* hover 图标 */
.menu-card:hover .el-icon {
  transform: scale(1.15);
}

/* hover 文字 */
.menu-card:hover span {
  color: #E64A19;
}

/* ===== 卡片文字 ===== */
.menu-card span {
  font-size: 18px;
  transition: 0.3s;
}
</style>