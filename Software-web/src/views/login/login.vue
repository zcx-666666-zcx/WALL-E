<script setup>
import { ref } from 'vue';
import { LoginApi } from '@/api/users.js';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';

const router = useRouter()
let log = ref("登 录")
let username = ref('');
let password = ref('');
let loading = ref(false);
let showPwd = ref(false);
let focusUser = ref(false);
let focusPwd = ref(false);

const GoToPage = (loginUser) => {
    const targetPath = loginUser.role === 'admin' ? '/admin' : '/index';
    router.replace({ path: targetPath, query: { username: loginUser.username } });
}
const GoToRegis = () => { router.push({ path: '/regis' }) }

const login = async () => {
    if (loading.value) return;
    if (!username.value || !password.value) { ElMessage.warning("请输入用户名和密码"); return; }
    loading.value = true;
    log.value = "登录中…";
    try {
        const loginInfo = { username: username.value, password: password.value };
        const result = await LoginApi(loginInfo);
        if (result.code) {
            log.value = "✓ 成功";
            localStorage.setItem('loginUserObject', JSON.stringify(result.data));
            localStorage.setItem('Id', result.data.id);
            setTimeout(() => GoToPage(result.data), 500);
        } else {
            ElMessage.error(result.msg || '登录失败');
        }
    } catch (error) {
        ElMessage.error(error?.response?.data?.msg || error?.message || '登录失败');
    } finally {
        loading.value = false;
        if (log.value !== "✓ 成功") {
            log.value = "登 录";
        }
    }
}

const handleKeydown = (e) => { if (e.key === 'Enter') login(); }
</script>

<template>
  <div class="login-root">

    <!-- 背景图 -->
    <div class="bg-image"></div>
    <!-- 暖色遮罩 -->
    <div class="bg-overlay"></div>
    <!-- 装饰光晕 -->
    <div class="bg-orb orb-1"></div>
    <div class="bg-orb orb-2"></div>
    <div class="bg-orb orb-3"></div>

    <!-- CSS 粒子 -->
    <div class="particles">
      <span v-for="n in 30" :key="n" class="particle" :style="{
        left: `${Math.random() * 100}%`,
        animationDelay: `${Math.random() * 8}s`,
        animationDuration: `${6 + Math.random() * 10}s`,
        width: `${2 + Math.random() * 3}px`,
        height: `${2 + Math.random() * 3}px`,
      }"></span>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">

      <!-- 左侧品牌区 -->
      <div class="card-brand">
        <div class="brand-inner">
          <div class="brand-logo">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
              <path d="M16 4C10 4 5 8.5 5 14c0 8 11 16 11 16s11-8 11-16c0-5.5-5-10-11-10z" fill="rgba(255,255,255,0.2)" stroke="white" stroke-width="1.5"/>
              <path d="M10 15h3.5l2-5 3 10 2-5H23" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h1 class="brand-name">智能陪伴</h1>
          <p class="brand-sub">机器人管理平台</p>
          <div class="brand-divider"></div>
          <p class="brand-desc">守护每一位长辈<br>让关爱触手可及</p>
          <div class="brand-features">
            <div class="feature-item" style="animation-delay:0.3s">
              <div class="feature-dot"></div>
              实时健康监测
            </div>
            <div class="feature-item" style="animation-delay:0.45s">
              <div class="feature-dot"></div>
              智能事件提醒
            </div>
            <div class="feature-item" style="animation-delay:0.6s">
              <div class="feature-dot"></div>
              AI 情感陪伴
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧表单区 -->
      <div class="card-form">
        <div class="form-inner">
          <div class="form-header">
            <h2 class="form-title">欢迎回来</h2>
            <p class="form-sub">请登录您的账户继续使用</p>
          </div>

          <div class="form-fields">
            <div class="field-group" :class="{ focused: focusUser }">
              <label class="field-label">用户名</label>
              <div class="field-wrap">
                <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <circle cx="8" cy="6" r="3" :stroke="focusUser ? '#FF6B40' : '#C4A898'" stroke-width="1.3"/>
                  <path d="M2 14c0-3.3 2.7-6 6-6s6 2.7 6 6" :stroke="focusUser ? '#FF6B40' : '#C4A898'" stroke-width="1.3" stroke-linecap="round"/>
                </svg>
                <input
                  class="field-input"
                  v-model="username"
                  type="text"
                  placeholder="请输入用户名"
                  @keydown="handleKeydown"
                  @focus="focusUser = true"
                  @blur="focusUser = false"
                  autocomplete="username"
                />
              </div>
            </div>

            <div class="field-group" :class="{ focused: focusPwd }">
              <label class="field-label">密码</label>
              <div class="field-wrap">
                <svg class="field-icon" width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <rect x="3" y="7" width="10" height="7" rx="1.5" :stroke="focusPwd ? '#FF6B40' : '#C4A898'" stroke-width="1.3"/>
                  <path d="M5 7V5a3 3 0 016 0v2" :stroke="focusPwd ? '#FF6B40' : '#C4A898'" stroke-width="1.3" stroke-linecap="round"/>
                  <circle cx="8" cy="10.5" r="1" :fill="focusPwd ? '#FF6B40' : '#C4A898'"/>
                </svg>
                <input
                  class="field-input"
                  v-model="password"
                  :type="showPwd ? 'text' : 'password'"
                  placeholder="请输入密码"
                  @keydown="handleKeydown"
                  @focus="focusPwd = true"
                  @blur="focusPwd = false"
                  autocomplete="current-password"
                />
                <button
                  class="pwd-toggle"
                  type="button"
                  @click="showPwd = !showPwd"
                  :title="showPwd ? '隐藏密码' : '显示密码'"
                >
                  <!-- 睁眼图标 -->
                  <svg v-if="showPwd" width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M2 8s2.5-4 6-4 6 4 6 4-2.5 4-6 4-6-4-6-4z" stroke="#A08070" stroke-width="1.3"/>
                    <circle cx="8" cy="8" r="2" stroke="#A08070" stroke-width="1.3"/>
                  </svg>
                  <!-- 闭眼图标 -->
                  <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M2 8s2.5-4 6-4 6 4 6 4-2.5 4-6 4-6-4-6-4z" stroke="#C4A898" stroke-width="1.3"/>
                    <circle cx="8" cy="8" r="1.5" fill="#C4A898"/>
                    <path d="M3 3l10 10" stroke="#C4A898" stroke-width="1.2" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <button
            class="login-btn"
            :class="{ loading: loading }"
            @click="login"
            :disabled="loading"
          >
            <span class="login-btn-text">{{ log }}</span>
            <div class="login-btn-shine"></div>
          </button>

          <div class="form-footer">
            <span class="footer-text">还没有账号？</span>
            <span class="footer-link" @click="GoToRegis">立即注册</span>
          </div>
        </div>
      </div>

    </div>

    <!-- 底部版权 -->
    <div class="page-footer">智能陪伴机器人管理平台 · 安全 · 贴心 · 专业</div>

  </div>
</template>

<style scoped>
/* ══ 根容器 ══ */
.login-root {
  width: 100vw; height: 100vh;
  display: flex; align-items: center; justify-content: center;
  position: relative; overflow: hidden;
  font-family: "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

/* 背景图 */
.bg-image {
  position: absolute; inset: 0;
  background-image: url("/images/index_picture2.png");
  background-image: image-set(
    url("/images/index_picture2.webp") type("image/webp"),
    url("/images/index_picture2.png") type("image/png")
  );
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  transform: scale(1.05);
  filter: brightness(0.75) saturate(0.9);
}

/* 暖色遮罩 */
.bg-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(
    135deg,
    rgba(80, 30, 10, 0.55) 0%,
    rgba(160, 70, 20, 0.35) 50%,
    rgba(40, 15, 5, 0.6) 100%
  );
}

/* 装饰光晕 */
.bg-orb {
  position: absolute; border-radius: 50%; pointer-events: none; filter: blur(80px);
}
.orb-1 {
  width: 600px; height: 600px; top: -200px; left: -150px;
  background: radial-gradient(circle, rgba(255,150,80,0.2) 0%, transparent 70%);
  animation: orbFloat 8s ease-in-out infinite;
}
.orb-2 {
  width: 500px; height: 500px; bottom: -150px; right: -100px;
  background: radial-gradient(circle, rgba(255,120,60,0.15) 0%, transparent 70%);
  animation: orbFloat 10s ease-in-out 2s infinite;
}
.orb-3 {
  width: 300px; height: 300px; top: 40%; left: 55%;
  background: radial-gradient(circle, rgba(255,180,120,0.1) 0%, transparent 70%);
  animation: orbFloat 9s ease-in-out 4s infinite;
}
@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%  { transform: translate(30px, -20px) scale(1.05); }
  66%  { transform: translate(-20px, 15px) scale(0.95); }
}

/* CSS 粒子 */
.particles {
  position: absolute; inset: 0; pointer-events: none; z-index: 5; overflow: hidden;
}
.particle {
  position: absolute; bottom: -10px;
  background: rgba(255, 200, 150, 0.5);
  border-radius: 50%;
  animation: rise linear infinite;
  box-shadow: 0 0 6px rgba(255, 180, 130, 0.4);
}
@keyframes rise {
  0%   { transform: translateY(0) scale(0); opacity: 0; }
  10%  { opacity: 1; }
  90%  { opacity: 0.6; }
  100% { transform: translateY(-100vh) scale(1); opacity: 0; }
}

/* ══ 登录卡片 ══ */
.login-card {
  position: relative; z-index: 10;
  width: min(900px, 90vw);
  height: min(520px, 85vh);
  display: flex;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 28px;
  overflow: hidden;
  backdrop-filter: blur(24px);
  box-shadow:
    0 32px 80px rgba(20,8,2,0.5),
    0 0 0 1px rgba(255,255,255,0.08) inset;
  animation: cardIn 0.7s cubic-bezier(0.34,1.4,0.64,1) both;
}
@keyframes cardIn {
  from { opacity:0; transform:translateY(32px) scale(0.96); }
  to   { opacity:1; transform:translateY(0) scale(1); }
}

/* ══ 左侧品牌 ══ */
.card-brand {
  width: 42%; flex-shrink: 0;
  background: linear-gradient(160deg, rgba(255,120,60,0.35) 0%, rgba(180,60,10,0.45) 100%);
  border-right: 1px solid rgba(255,255,255,0.1);
  display: flex; align-items: center; justify-content: center;
  padding: 48px 40px;
  position: relative; overflow: hidden;
}
.card-brand::before {
  content: '';
  position: absolute; top: -60px; right: -60px;
  width: 220px; height: 220px; border-radius: 50%;
  background: rgba(255,200,150,0.08); pointer-events: none;
  animation: brandGlow 6s ease-in-out infinite;
}
.card-brand::after {
  content: '';
  position: absolute; bottom: -40px; left: -40px;
  width: 160px; height: 160px; border-radius: 50%;
  background: rgba(255,160,100,0.06); pointer-events: none;
  animation: brandGlow 8s ease-in-out 2s infinite;
}
@keyframes brandGlow {
  0%, 100% { transform: scale(1); opacity: 1; }
  50%  { transform: scale(1.2); opacity: 0.6; }
}

.brand-inner { display: flex; flex-direction: column; align-items: flex-start; gap: 0; position: relative; z-index: 1; }

.brand-logo {
  width: 60px; height: 60px; border-radius: 18px;
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.25);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  animation: logoPulse 3s ease-in-out infinite;
}
@keyframes logoPulse {
  0%, 100% { box-shadow: 0 8px 24px rgba(0,0,0,0.2); }
  50%  { box-shadow: 0 8px 32px rgba(255,140,80,0.3); }
}

.brand-name {
  font-size: 32px; font-weight: 800; color: white;
  letter-spacing: -0.01em; margin: 0 0 4px; line-height: 1;
  animation: fadeSlideIn 0.6s ease both 0.1s;
}
.brand-sub {
  font-size: 14px; color: rgba(255,255,255,0.65);
  margin: 0 0 20px; letter-spacing: 0.04em;
  animation: fadeSlideIn 0.6s ease both 0.15s;
}
.brand-divider {
  width: 40px; height: 2px; border-radius: 1px;
  background: linear-gradient(90deg, rgba(255,200,150,0.8), transparent);
  margin-bottom: 16px;
  animation: dividerGrow 0.6s ease both 0.2s;
}
@keyframes dividerGrow {
  from { width: 0; opacity: 0; }
  to   { width: 40px; opacity: 1; }
}
.brand-desc {
  font-size: 13.5px; color: rgba(255,255,255,0.55);
  line-height: 1.8; margin: 0 0 24px;
  animation: fadeSlideIn 0.6s ease both 0.25s;
}
@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.brand-features { display: flex; flex-direction: column; gap: 10px; }
.feature-item {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: rgba(255,255,255,0.7);
  animation: fadeSlideIn 0.5s ease both;
}
.feature-dot {
  width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0;
  background: rgba(255,200,150,0.9);
  box-shadow: 0 0 6px rgba(255,200,150,0.5);
  animation: dotGlow 2s ease-in-out infinite;
}
@keyframes dotGlow {
  0%, 100% { box-shadow: 0 0 6px rgba(255,200,150,0.5); }
  50%  { box-shadow: 0 0 12px rgba(255,200,150,0.9); }
}

/* ══ 右侧表单 ══ */
.card-form {
  flex: 1;
  background: rgba(255,252,248,0.96);
  display: flex; align-items: center; justify-content: center;
  padding: 48px 44px;
}

.form-inner { width: 100%; max-width: 320px; }

.form-header { margin-bottom: 32px; }
.form-title {
  font-size: 24px; font-weight: 800; color: #2A1408;
  letter-spacing: -0.01em; margin: 0 0 6px;
}
.form-sub { font-size: 13px; color: #B09080; margin: 0; }

/* 表单字段 */
.form-fields { display: flex; flex-direction: column; gap: 16px; margin-bottom: 24px; }

.field-group { display: flex; flex-direction: column; gap: 6px; }
.field-label { font-size: 12.5px; font-weight: 600; color: #6A4030; transition: color 0.2s; }
.field-group.focused .field-label { color: #E06030; }

.field-wrap { position: relative; display: flex; align-items: center; }
.field-icon {
  position: absolute; left: 12px; pointer-events: none; flex-shrink: 0; z-index: 1;
  transition: all 0.2s;
}

.field-input {
  width: 100%; height: 44px;
  padding: 0 40px 0 38px;
  border: 1.5px solid rgba(255,160,120,0.25);
  border-radius: 12px;
  font-size: 14px; font-family: inherit;
  color: #3A2010; background: #FFFAF7;
  outline: none; box-sizing: border-box;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
}
.field-input:focus {
  border-color: #FF8A65; background: #FFFFFF;
  box-shadow: 0 0 0 3px rgba(255,138,101,0.12);
}
.field-input::placeholder { color: #C4A898; }

/* 密码显隐按钮 */
.pwd-toggle {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  width: 30px; height: 30px; border-radius: 8px;
  border: none; background: transparent;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; z-index: 1;
  transition: background 0.18s;
}
.pwd-toggle:hover { background: rgba(255,140,90,0.1); }

/* 登录按钮 */
.login-btn {
  width: 100%; height: 48px;
  background: linear-gradient(90deg, #FF9A76, #FF5A30);
  color: white; border: none; border-radius: 12px;
  font-size: 15px; font-weight: 700; font-family: inherit;
  cursor: pointer; transition: all 0.25s ease;
  box-shadow: 0 6px 20px rgba(255,90,48,0.35);
  position: relative; overflow: hidden;
  letter-spacing: 0.06em;
}
.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(255,90,48,0.45);
}
.login-btn:active:not(:disabled) { transform: scale(0.97); }
.login-btn:disabled { opacity: 0.75; cursor: not-allowed; }
.login-btn.loading { background: linear-gradient(90deg, #FFB090, #FF8060); }

/* 按钮光泽扫光 */
.login-btn-shine {
  position: absolute; top: 0; left: -100%; width: 60%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transform: skewX(-20deg);
  animation: shine 3s ease infinite;
}
@keyframes shine {
  0%   { left: -100%; }
  40%  { left: 140%; }
  100% { left: 140%; }
}
.login-btn-text { position: relative; z-index: 1; }

/* 底部注册 */
.form-footer {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  margin-top: 20px; font-size: 13px;
}
.footer-text { color: #B09080; }
.footer-link {
  color: #E07040; font-weight: 600; cursor: pointer;
  transition: color 0.18s;
  text-decoration: underline; text-underline-offset: 2px; text-decoration-color: rgba(224,112,64,0.4);
}
.footer-link:hover { color: #C05020; }

/* 底部版权 */
.page-footer {
  position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
  font-size: 11.5px; color: rgba(255,255,255,0.35);
  white-space: nowrap; z-index: 10; letter-spacing: 0.04em;
}

/* ══ 响应式 ══ */
@media (max-width: 768px) {
  .login-card {
    flex-direction: column; width: min(400px, 94vw);
    height: auto; min-height: 85vh;
  }
  .card-brand { width: 100%; padding: 32px 28px; }
  .card-brand::before, .card-brand::after { display: none; }
  .brand-inner { align-items: center; text-align: center; }
  .brand-divider { margin: 0 auto 16px; }
  .brand-features { align-items: center; }
  .brand-logo { margin-bottom: 12px; }
  .brand-name { font-size: 24px; }
  .brand-desc { margin-bottom: 16px; }
  .card-form { padding: 32px 28px; }
  .form-inner { max-width: 100%; }
  .form-title { font-size: 20px; }
  .page-footer { font-size: 10px; bottom: 10px; }
}
</style>
